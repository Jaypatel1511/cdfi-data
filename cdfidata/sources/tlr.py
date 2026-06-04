"""
TLR (Transaction Level Report) data loader.
Downloads, cleans, and returns CDFI Fund transaction-level loan data.
"""
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Optional

from cdfidata.pipeline.downloader import download_tlr, extract_zip, cache_path
from cdfidata.pipeline.cleaner import standardize
from cdfidata.pipeline.exporter import to_csv, to_sqlite, to_parquet
from cdfidata.utils.schema import (
    TLR_COLUMNS, TLR_DTYPES, STATE_FIPS,
    ACPR_COLUMNS, TLR_COLUMNS_BY_YEAR, TLR_CANONICAL, TLR_URLS, TLR_SENTINELS,
)


def _derive_state(df):
    """Derive 'state' from fips_code, normalizing FIPS first.

    ACPR public files (FY2020/FY2021) strip the leading zero from FIPS for states
    01-09, so those codes arrive 10-digit instead of 11; pad to 11 so the 2-digit
    state prefix is correct. No-op on FY2022 (already 11-digit). Corrects both
    fips_code and the derived state.
    """
    if "fips_code" in df.columns:
        fips = df["fips_code"].astype("string").str.strip()
        fips = fips.mask(fips == "", pd.NA).str.zfill(11)
        df["state"] = fips.str[:2].map(STATE_FIPS)
        df["fips_code"] = fips.astype(object)
    else:
        df["state"] = pd.NA
    return df


def _null_sentinels(df):
    """Replace documented CDFI Fund 'not reported / not applicable' codes with NaN.

    Field-specific: for each (col, codes) in TLR_SENTINELS, only the codes the TLR Data
    Point Guidance (Feb 2022) documents as not-reported for that field are nulled, matched
    against the column's ACTUAL dtype. naics_code may arrive as str ("999999") or numeric
    (999999) depending on era/cast — both are handled. Nulls cells to NaN only; never drops
    rows. Expects canonical column names (call after reindex to TLR_CANONICAL).
    """
    for col, codes in TLR_SENTINELS.items():
        if col not in df.columns:
            continue
        series = df[col]
        if pd.api.types.is_numeric_dtype(series):
            match = set(codes)
        elif series.dtype == object or pd.api.types.is_string_dtype(series):
            match = {str(c) for c in codes}
        else:
            print(f"[_null_sentinels] WARNING: {col} has unexpected dtype "
                  f"{series.dtype!r}; matching both numeric and str forms of {codes}")
            match = set(codes) | {str(c) for c in codes}
        df[col] = series.mask(series.isin(match), np.nan)
    return df


class TLRLoader:
    """
    Loader for CDFI Fund Transaction Level Report (TLR) data.

    Usage:
        loader = TLRLoader()
        df = loader.load(year=2022)
        df_il = loader.filter_state("IL")
    """

    def __init__(self):
        self._df: Optional[pd.DataFrame] = None
        self._year: Optional[int] = None

    def load(self, year: int = 2022, force: bool = False,
             url: Optional[str] = None) -> pd.DataFrame:
        """
        Download and load TLR data for a given fiscal year.

        Args:
            year:  Fiscal year e.g. 2022
            force: Re-download even if cached
            url:   Optional explicit URL passed through to download_tlr.

        Returns:
            Clean pandas DataFrame with standardized columns
        """
        self._year = year

        # Download zip
        zip_path = download_tlr(year, force=force, url=url)

        # Extract
        extracted = extract_zip(zip_path)
        tlr_files = [f for f in extracted if "TLR" in str(f).upper()
                     and str(f).endswith(".csv")]

        if not tlr_files:
            # Try finding CSV directly in cache
            tlr_files = list(cache_path("").parent.glob(f"*TLR*{year}*.csv"))

        if not tlr_files:
            raise FileNotFoundError(
                f"Could not find TLR CSV file in extracted archive for FY{year}. "
                f"Extracted files: {extracted}"
            )

        csv_path = tlr_files[0]
        print(f"Loading TLR data from {csv_path}...")

        try:
            df = pd.read_csv(csv_path, dtype=str, low_memory=False)
        except UnicodeDecodeError:
            df = pd.read_csv(csv_path, dtype=str, low_memory=False,
                             encoding="latin-1")
        print(f"Raw records: {len(df):,}")

        col_map = TLR_COLUMNS_BY_YEAR.get(year, TLR_COLUMNS)
        df = standardize(df, col_map, TLR_DTYPES, required_cols=["amount"])
        df = df.reindex(columns=TLR_CANONICAL)   # ensure all 61; NaN-fill era-specific (award_category for ACPR); drop strays
        df = _null_sentinels(df)                  # field-specific not-reported codes → NaN; independent of _derive_state
        df["source_release"] = f"FY{year}"
        df = _derive_state(df)                    # adds 'state' from fips_code (already defined)
        self._df = df
        return df

    def load_range(self, start: int, end: int, force: bool = False) -> pd.DataFrame:
        """Load and stack all available TLR years in [start, end] (inclusive).

        Frames are concatenated as-is (no dedup); use fiscal_year + source_release to
        identify late-submission overlaps between releases.

        Overlap & completeness guidance: releases overlap on fiscal_year — FY2022 (AMIS)
        restates/expands prior-year (FY2021) data, so the same fiscal_year can appear in more
        than one release. Filter by source_release and prefer the latest release for a given
        fiscal_year; do NOT sum/aggregate the full stacked frame naively — that double-counts
        restated rows. Field completeness (rate/term/NAICS especially) is era-dependent, so a
        single statistic across the full frame is confounded by reporting era. See
        docs/CANONICAL_SCHEMA.md.
        """
        years = [y for y in sorted(TLR_URLS) if start <= y <= end]
        if not years:
            raise ValueError(
                f"No TLR data available in range {start}-{end}. "
                f"Available years: {sorted(TLR_URLS)}"
            )
        frames = [self.load(year=y, force=force) for y in years]
        df = pd.concat(frames, ignore_index=True)
        self._df = df
        self._year = None
        print(f"Cumulative: {len(df):,} rows across {len(years)} releases {years}")
        return df

    def load_cumulative(self, force: bool = False) -> pd.DataFrame:
        """Load and stack every available TLR year (no dedup). See load_range.

        Overlap & completeness guidance: releases overlap on fiscal_year — FY2022 (AMIS)
        restates/expands prior-year (FY2021) data; filter by source_release and prefer the
        latest release for a given fiscal_year. Do NOT sum/aggregate the full frame naively
        (double-counts restated rows); field completeness (rate/term/NAICS) is era-dependent.
        See docs/CANONICAL_SCHEMA.md.
        """
        years = sorted(TLR_URLS)
        return self.load_range(years[0], years[-1], force=force)

    def load_sample(self, n: int = 1000) -> pd.DataFrame:
        """
        Generate synthetic TLR sample data for testing and demos.
        Does not require downloading real data.

        Args:
            n: Number of sample records

        Returns:
            Synthetic DataFrame with the legacy sample schema

        NOTE: load_sample is a LEGACY SYNTHETIC FIXTURE. Its schema does NOT match the real
        63-column output of load()/load_cumulative() (which return the unified canonical TLR
        schema + provenance). It exists only for offline demos/tests; real analysis should use
        load()/load_cumulative().
        """
        import numpy as np
        import random
        random.seed(42)
        np.random.seed(42)

        states = ["IL", "NY", "CA", "TX", "GA", "NC", "OH", "PA", "FL", "MI"]
        loan_types = ["Business Loan", "Microenterprise Loan", "Home Mortgage",
                      "Home Improvement", "Consumer Loan", "Commercial RE"]
        purposes = ["Job Creation", "Affordable Housing", "Small Business",
                    "Community Facility", "Microenterprise"]
        programs = ["FA", "NACA", "RRP"]

        records = []
        for i in range(n):
            records.append({
                "fiscal_year": random.choice([2020, 2021, 2022]),
                "award_number": f"FA-{i:06d}",
                "financing_type": "Loan",
                "loan_type": random.choice(loan_types),
                "purpose": random.choice(purposes),
                "amount": round(np.random.lognormal(10, 1.5)),
                "term_months": random.choice([12, 24, 36, 60, 84, 120]),
                "interest_rate": round(np.random.uniform(0.02, 0.08), 4),
                "state": random.choice(states),
                "census_tract": f"{random.randint(1000, 9999):04d}",
                "low_income_area": random.choice([True, False]),
                "distressed_area": random.choice([True, False]),
                "minority_borrower": random.choice([True, False]),
                "women_borrower": random.choice([True, False]),
                "jobs_created": random.randint(0, 50),
                "jobs_retained": random.randint(0, 100),
                "program": random.choice(programs),
            })

        self._df = pd.DataFrame(records)
        return self._df

    def filter_state(self, state: str) -> pd.DataFrame:
        """Filter loaded data to a specific state."""
        self._check_loaded()
        return self._df[self._df["state"] == state.upper()].copy()

    def filter_loan_type(self, loan_type: str) -> pd.DataFrame:
        """Filter by partial match on transaction_type (real schema) or loan_type (sample)."""
        self._check_loaded()
        col = "transaction_type" if "transaction_type" in self._df.columns else "loan_type"
        return self._df[
            self._df[col].str.contains(loan_type, case=False, na=False)
        ].copy()

    def filter_amount(self, min_amount: float = 0,
                      max_amount: float = float("inf")) -> pd.DataFrame:
        """Filter by loan amount range."""
        self._check_loaded()
        return self._df[
            (self._df["amount"] >= min_amount) &
            (self._df["amount"] <= max_amount)
        ].copy()

    def _release_breakdown(self, df) -> pd.DataFrame:
        """Per-source_release records + total amount.

        Uses the SAME amount column summary() reports on. Per-release amounts are safe;
        the double-count footgun only arises from summing ACROSS overlapping releases.
        """
        g = df.groupby("source_release", dropna=False)
        return pd.DataFrame({
            "records": g.size(),
            "total_amount": g["amount"].sum(),
        })

    def summary(self) -> pd.DataFrame:
        """Return a summary of the loaded TLR data.

        Multi-release-aware: after load_cumulative()/load_range() the stored frame stacks
        overlapping releases (same fiscal_year restated across vintages), so a single
        cross-release "Total amount" double-counts restated rows. In that case summary()
        prints a per-source_release breakdown plus an overlap caveat instead of a misleading
        grand total. Single-release/single-year loads are unchanged.
        """
        self._check_loaded()
        df = self._df
        multi = "source_release" in df.columns and df["source_release"].nunique() > 1

        if not multi:
            print(f"\nTLR Data Summary — FY{self._year}")
            print(f"  Total records:      {len(df):,}")
            print(f"  Total amount:       ${df['amount'].sum()/1e9:.2f}B")
            print(f"  Median loan size:   ${df['amount'].median():,.0f}")
            print(f"  States covered:     {df['state'].nunique()}")
            if "jobs_created" in df.columns:
                print(f"  Total jobs created: {df['jobs_created'].sum():,.0f}")
            print()
            return df.describe()

        breakdown = self._release_breakdown(df)
        releases = list(breakdown.index)
        print(f"\nTLR Data Summary — {len(releases)} releases ({', '.join(map(str, releases))})")
        print("  CAVEAT: releases overlap on fiscal_year; cross-release totals are NOT additive")
        print("  (restated years double-counted) — filter by source_release for a single-vintage total.")
        print(f"  Total records:      {len(df):,}")
        print("  Per source_release:")
        for rel, row in breakdown.iterrows():
            print(f"    {rel}:  {int(row['records']):,} records,  "
                  f"${row['total_amount']/1e9:.2f}B")
        print()
        return breakdown

    def to_csv(self, path: str) -> None:
        self._check_loaded()
        to_csv(self._df, path)

    def to_sqlite(self, db_path: str, table: str = "tlr") -> None:
        self._check_loaded()
        to_sqlite(self._df, db_path, table)

    def to_parquet(self, path: str) -> None:
        self._check_loaded()
        to_parquet(self._df, path)

    def _check_loaded(self) -> None:
        if self._df is None:
            raise RuntimeError(
                "No data loaded. Call .load(year=2022) or .load_sample() first."
            )
