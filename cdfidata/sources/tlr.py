"""
TLR (Transaction Level Report) data loader.
Downloads, cleans, and returns CDFI Fund transaction-level loan data.
"""
import pandas as pd
from pathlib import Path
from typing import Optional

from cdfidata.pipeline.downloader import download_tlr, extract_zip, cache_path
from cdfidata.pipeline.cleaner import standardize
from cdfidata.pipeline.exporter import to_csv, to_sqlite, to_parquet
from cdfidata.utils.schema import TLR_COLUMNS, TLR_DTYPES


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

    def load(self, year: int = 2022, force: bool = False) -> pd.DataFrame:
        """
        Download and load TLR data for a given fiscal year.

        Args:
            year:  Fiscal year e.g. 2022
            force: Re-download even if cached

        Returns:
            Clean pandas DataFrame with standardized columns
        """
        self._year = year

        # Download zip
        zip_path = download_tlr(year, force=force)

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

        df = pd.read_csv(csv_path, dtype=str, low_memory=False)
        print(f"Raw records: {len(df):,}")

        df = standardize(df, TLR_COLUMNS, TLR_DTYPES,
                         required_cols=["amount"])

        print(f"Clean records: {len(df):,}")
        self._df = df
        return df

    def load_sample(self, n: int = 1000) -> pd.DataFrame:
        """
        Generate synthetic TLR sample data for testing and demos.
        Does not require downloading real data.

        Args:
            n: Number of sample records

        Returns:
            Synthetic DataFrame with TLR schema
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
        """Filter by loan type (partial match)."""
        self._check_loaded()
        return self._df[
            self._df["loan_type"].str.contains(loan_type, case=False, na=False)
        ].copy()

    def filter_amount(self, min_amount: float = 0,
                      max_amount: float = float("inf")) -> pd.DataFrame:
        """Filter by loan amount range."""
        self._check_loaded()
        return self._df[
            (self._df["amount"] >= min_amount) &
            (self._df["amount"] <= max_amount)
        ].copy()

    def summary(self) -> pd.DataFrame:
        """Return a summary of the loaded TLR data."""
        self._check_loaded()
        df = self._df
        print(f"\nTLR Data Summary — FY{self._year}")
        print(f"  Total records:      {len(df):,}")
        print(f"  Total amount:       ${df['amount'].sum()/1e9:.2f}B")
        print(f"  Median loan size:   ${df['amount'].median():,.0f}")
        print(f"  States covered:     {df['state'].nunique()}")
        if "jobs_created" in df.columns:
            print(f"  Total jobs created: {df['jobs_created'].sum():,.0f}")
        print()
        return df.describe()

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
