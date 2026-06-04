import re
from pathlib import Path

import pytest
import pandas as pd
from cdfidata.sources.tlr import TLRLoader
from cdfidata.pipeline import downloader

DOCS_CANONICAL = Path(__file__).resolve().parents[1] / "docs" / "CANONICAL_SCHEMA.md"


def test_load_sample_returns_dataframe():
    loader = TLRLoader()
    df = loader.load_sample(n=100)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 100


def test_load_sample_has_required_columns():
    loader = TLRLoader()
    df = loader.load_sample(n=100)
    required = ["fiscal_year", "amount", "state", "loan_type", "purpose"]
    for col in required:
        assert col in df.columns


def test_load_sample_amounts_positive():
    loader = TLRLoader()
    df = loader.load_sample(n=100)
    assert (df["amount"] > 0).all()


def test_filter_state(tlr_loader):
    df = tlr_loader.filter_state("IL")
    assert all(df["state"] == "IL")


def test_filter_state_empty(tlr_loader):
    df = tlr_loader.filter_state("ZZ")
    assert len(df) == 0


def test_filter_loan_type(tlr_loader):
    df = tlr_loader.filter_loan_type("Business")
    assert all(df["loan_type"].str.contains("Business", case=False))


def test_filter_amount(tlr_loader):
    df = tlr_loader.filter_amount(min_amount=10_000, max_amount=100_000)
    assert all(df["amount"] >= 10_000)
    assert all(df["amount"] <= 100_000)


def test_not_loaded_raises():
    loader = TLRLoader()
    with pytest.raises(RuntimeError, match="No data loaded"):
        loader.filter_state("IL")


def test_summary_runs(tlr_loader):
    tlr_loader.summary()


def test_to_csv(tlr_loader, tmp_path):
    path = str(tmp_path / "tlr.csv")
    tlr_loader.to_csv(path)
    df = pd.read_csv(path)
    assert len(df) == 500


def test_to_sqlite(tlr_loader, tmp_path):
    path = str(tmp_path / "tlr.db")
    tlr_loader.to_sqlite(path, table="tlr")
    import sqlite3
    with sqlite3.connect(path) as conn:
        df = pd.read_sql("SELECT * FROM tlr", conn)
    assert len(df) == 500


def test_download_file_sends_user_agent(monkeypatch, tmp_path):
    captured = {}

    class FakeResponse:
        headers = {"content-length": "0"}

        def raise_for_status(self):
            pass

        def iter_content(self, chunk_size=8192):
            return iter([])

    def fake_get(url, **kwargs):
        captured["headers"] = kwargs.get("headers")
        return FakeResponse()

    monkeypatch.setattr(downloader, "get_cache_dir", lambda: tmp_path)
    monkeypatch.setattr(downloader.requests, "get", fake_get)

    downloader.download_file("https://example.com/x.zip", "x.zip", force=True)

    assert captured["headers"] is not None
    assert "User-Agent" in captured["headers"]


def test_derive_state_from_fips():
    import pandas as pd
    from cdfidata.sources.tlr import _derive_state
    df = _derive_state(pd.DataFrame({"fips_code": ["23003952100", "17031010100", "99999999999", None]}))
    out = df["state"].tolist()
    assert out[0] == "ME" and out[1] == "IL"
    assert pd.isna(out[2]) and pd.isna(out[3])


def test_fips_leading_zero_padding():
    import pandas as pd
    from cdfidata.sources.tlr import _derive_state
    df = _derive_state(pd.DataFrame({"fips_code": ["6037204200", "1001020100", "23003952100", "", None]}))
    assert df["fips_code"].iloc[0] == "06037204200"          # CA tract, leading zero recovered
    states = df["state"].tolist()
    assert states[0] == "CA" and states[1] == "AL" and states[2] == "ME"
    assert pd.isna(states[3]) and pd.isna(states[4])         # empty and missing -> NaN


def test_tlr_columns_cover_real_headers():
    REAL_TLR_HEADERS = [
     "org_id","trans_id","tlr_submission_year__c","original_loan_investment_amount_","fipscode_2010",
     "investee_type__c","date_originated__c","purpose__c","transaction_type__c","interest_rate__c",
     "interest_type__c","points__c","origination_fees__c","amortization_type__c","equity_like_features__c",
     "term_in_months__c","guarantee__c","type_of_jobs_reported__c","source_of_job_estimates__c",
     "source_of_job_estimates_other__c","community_facility__c","desc_of_other_approved_otp_end_u",
     "forgivable_loan__c","naics_name","date_business_established__c","entity_structure__c",
     "minority_owned_or_controlled__c","women_owned_or_controlled__c","description_of_the_other_approve",
     "low_income_owned_or_controlled__","low_income_status__c","other_targeted_populations__c",
     "litp_end_users__c","otp_end_users__c","ia_end_users__c","gender__c","race__c","hispanic_origin__c",
     "female_headed_household__c","first_time_home_buyer__c","capacity_of_educational_communit",
     "capacity_of_childcare_community_","capacity_of_healthcare_community","capacity_of_arts_center_communit",
     "capacity_of_other_community_faci","square_feet_of_real_estate_total","square_feet_of_real_estate_manuf",
     "square_feet_of_real_estate_offic","square_feet_of_real_estate_retai","affordable_housing_units_sale__c",
     "affordable_housing_units_rental_","loan_status__c","banked_at_time_of_intake__c",
     "annual_gross_revenue_from_busine","total_project_cost__c","proj_perm_jobs_to_be_created_fin",
     "proj_perm_jobs_created_tenant_bu","projected_jobs_to_be_created_con","housing_units_sale__c",
     "housing_units_rental__c","AwardCategory",
    ]
    from cdfidata.utils.schema import TLR_COLUMNS
    missing = [h for h in REAL_TLR_HEADERS if h.upper() not in TLR_COLUMNS]
    assert not missing, f"unmapped real headers: {missing}"


def test_download_tlr_uses_passed_url(monkeypatch):
    captured = {}

    def fake_download_file(url, filename, force=False):
        captured["url"] = url
        captured["filename"] = filename
        return url

    monkeypatch.setattr(downloader, "download_file", fake_download_file)

    downloader.download_tlr(2022, url="https://example.com/x.zip")

    assert captured["url"] == "https://example.com/x.zip"


def test_canonical_matches_maps():
    from cdfidata.utils.schema import TLR_CANONICAL, ACPR_COLUMNS, TLR_COLUMNS
    assert len(TLR_CANONICAL) == 61 and len(set(TLR_CANONICAL)) == 61
    assert set(TLR_CANONICAL) == set(ACPR_COLUMNS.values()) | set(TLR_COLUMNS.values())
    assert "naics_code" in TLR_CANONICAL and "naics_name" not in TLR_CANONICAL


@pytest.mark.live
def test_real_headers_map_live():
    import pandas as pd, io, zipfile, requests, glob, os, tempfile
    from cdfidata.utils.schema import TLR_URLS, TLR_COLUMNS_BY_YEAR
    cols_by_year = {}
    for year, url in TLR_URLS.items():
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=180); r.raise_for_status()
        d = tempfile.mkdtemp()
        zipfile.ZipFile(io.BytesIO(r.content)).extractall(d)
        tlr = [p for p in glob.glob(d + "/**/*", recursive=True)
               if "tlr" in os.path.basename(p).lower() and p.lower().endswith(".csv")][0]
        cols = pd.read_csv(tlr, nrows=0).columns.tolist()
        cols_by_year[year] = cols
        missing = [c for c in cols if c.upper() not in TLR_COLUMNS_BY_YEAR[year]]
        assert not missing, f"FY{year} headers not in map: {missing}"
    assert set(cols_by_year[2020]) == set(cols_by_year[2021]), "FY2020 != FY2021 header set"


def test_load_range_empty_raises():
    import pytest
    from cdfidata.sources.tlr import TLRLoader
    with pytest.raises(ValueError):
        TLRLoader().load_range(1990, 1995)


def test_schema_doc_matches_canonical():
    """Anti-drift guard (offline): every canonical column name must be documented in
    docs/CANONICAL_SCHEMA.md. A renamed/removed canonical column with no doc update fails.

    Uses a word-boundary match (\\bname\\b) rather than a plain substring test: some
    canonical names are substrings of others (e.g. 'amount' inside 'original_amount' as
    referenced in the sentinel section), so a naive `name in text` would mask real drift.
    `_` is a regex word char, so \\bamount\\b does NOT match inside 'original_amount'.
    """
    from cdfidata.utils.schema import TLR_CANONICAL
    assert DOCS_CANONICAL.exists(), f"missing {DOCS_CANONICAL}"
    text = DOCS_CANONICAL.read_text()
    missing = [c for c in TLR_CANONICAL if not re.search(rf"\b{re.escape(c)}\b", text)]
    assert not missing, f"canonical columns not documented in CANONICAL_SCHEMA.md: {missing}"


@pytest.mark.live
def test_cumulative_lossless():
    """Live: load_cumulative is a lossless stack with correct per-release provenance.

    No hardcoded row counts — the CDFI Fund restates data, so counts are data, not spec.
    Years are the fixed scope; counts come from the loader at run time.
    """
    years = [2020, 2021, 2022]
    loader = TLRLoader()
    per_year = {y: len(loader.load(year=y)) for y in years}
    cum = TLRLoader().load_cumulative()

    # losslessness: stacked length == sum of per-year lengths (no dedup, nothing dropped)
    assert len(cum) == sum(per_year.values()), (
        f"cum={len(cum):,} != sum(per_year)={sum(per_year.values()):,}; per_year={per_year}"
    )

    # provenance: rows tagged FY{year} match that year's standalone load count
    for y in years:
        label = f"FY{y}"                       # source_release label format from load()
        got = int((cum["source_release"] == label).sum())
        assert got == per_year[y], (
            f"{label}: cum has {got:,} rows, standalone load(year={y}) had {per_year[y]:,}"
        )

    # naics_code must not mix ACPR-str vs AMIS-numeric after stacking + sentinel nulling
    nonnull = cum["naics_code"].dropna()
    pytypes = {type(v).__name__ for v in nonnull}
    print(f"\nload_cumulative naics_code observed dtype={cum['naics_code'].dtype!r}, "
          f"non-null python types={pytypes}")
    assert len(pytypes) <= 1, (
        f"naics_code mixes python types across the stacked frame: {pytypes} "
        f"(dtype={cum['naics_code'].dtype!r})"
    )


def _sentinel_match_count(series, codes):
    """Count cells in `series` equal to any code, matched to the column's actual dtype.

    Mirrors _null_sentinels' dtype handling so 'raw count' lines up with what gets nulled.
    """
    if pd.api.types.is_numeric_dtype(series):
        match = set(codes)
    elif series.dtype == object or pd.api.types.is_string_dtype(series):
        match = {str(c) for c in codes}
    else:
        match = set(codes) | {str(c) for c in codes}
    return int(series.isin(match).sum())


def test_null_sentinels_field_specific():
    """Offline regression guard: only documented codes are nulled, look-alike reals survive."""
    import numpy as np
    from cdfidata.sources.tlr import _null_sentinels

    df = pd.DataFrame({
        "interest_rate": [99.0, 0.0, 1.0, 18.0, 5.5],     # idx0 sentinel; rest real (incl. 0/1/18)
        "term_months":   [999.0, 6.0, 360.0, 120.0, 999.0],  # idx0,4 sentinel; 6/360 real
        "points":        [99.0, 100.0, 0.0, 2.5, 99.0],   # idx0,4 sentinel; 100 is range ceiling (keep)
        "naics_code":    ["999999", "522110", "236220", "999999", "611310"],  # str era
    })
    out = _null_sentinels(df.copy())

    # nulled → NaN
    assert pd.isna(out["interest_rate"].iloc[0])
    assert pd.isna(out["term_months"].iloc[0]) and pd.isna(out["term_months"].iloc[4])
    assert pd.isna(out["points"].iloc[0]) and pd.isna(out["points"].iloc[4])
    assert pd.isna(out["naics_code"].iloc[0]) and pd.isna(out["naics_code"].iloc[3])

    # PRESERVED — must NOT be nulled
    assert out["interest_rate"].iloc[1] == 0.0
    assert out["interest_rate"].iloc[2] == 1.0
    assert out["interest_rate"].iloc[3] == 18.0
    assert out["interest_rate"].iloc[4] == 5.5
    assert out["term_months"].iloc[1] == 6.0 and out["term_months"].iloc[2] == 360.0
    assert out["points"].iloc[1] == 100.0          # range ceiling, NOT a not-reported code
    assert out["points"].iloc[2] == 0.0 and out["points"].iloc[3] == 2.5
    assert out["naics_code"].iloc[1] == "522110"   # a normal NAICS code survives

    # naics_code may also arrive numeric — handle 999999 (int) and preserve a real code
    num = _null_sentinels(pd.DataFrame({"naics_code": [999999, 522110]}))
    assert pd.isna(num["naics_code"].iloc[0]) and num["naics_code"].iloc[1] == 522110


@pytest.mark.live
def test_sentinels_absent_on_real_data():
    """Live: on FY2022 (AMIS) and FY2020 (ACPR), sentinels are gone post-load and the
    post-load NaN rise equals exactly the raw sentinel count for each field."""
    from cdfidata.sources.tlr import TLRLoader
    from cdfidata.pipeline.downloader import download_tlr, extract_zip
    from cdfidata.pipeline.cleaner import standardize
    from cdfidata.utils.schema import (
        TLR_SENTINELS, TLR_COLUMNS_BY_YEAR, TLR_COLUMNS, TLR_DTYPES, TLR_CANONICAL,
    )

    def prenull_frame(year):
        """The standardized+reindexed frame as it exists immediately BEFORE _null_sentinels."""
        zip_path = download_tlr(year)
        extracted = extract_zip(zip_path)
        tlr_files = [f for f in extracted if "TLR" in str(f).upper() and str(f).endswith(".csv")]
        if not tlr_files:
            from cdfidata.pipeline.downloader import cache_path
            tlr_files = list(cache_path("").parent.glob(f"*TLR*{year}*.csv"))
        csv_path = tlr_files[0]
        try:
            raw = pd.read_csv(csv_path, dtype=str, low_memory=False)
        except UnicodeDecodeError:
            raw = pd.read_csv(csv_path, dtype=str, low_memory=False, encoding="latin-1")
        col_map = TLR_COLUMNS_BY_YEAR.get(year, TLR_COLUMNS)
        df = standardize(raw, col_map, TLR_DTYPES, required_cols=["amount"])
        return df.reindex(columns=TLR_CANONICAL)

    for year in (2022, 2020):
        pre = prenull_frame(year)
        df = TLRLoader().load(year=year)
        n = len(df)
        print(f"\n── FY{year} sentinel nulling ──  rows={n:,}")
        for col, codes in TLR_SENTINELS.items():
            code = next(iter(codes))
            # sentinel absent post-load (dtype-aware, so naics str/num both covered)
            assert _sentinel_match_count(df[col], codes) == 0, \
                f"FY{year}: {col}=={code} still present after load()"
            # NaN rose by EXACTLY the raw count of that sentinel — nothing more
            raw_count = _sentinel_match_count(pre[col], codes)
            nan_before = int(pre[col].isna().sum())
            nan_after = int(df[col].isna().sum())
            delta = nan_after - nan_before
            assert delta == raw_count, (
                f"FY{year} {col}: NaN rose by {delta}, expected raw sentinel count {raw_count}"
            )
            share = (100.0 * raw_count / n) if n else 0.0
            print(f"  {col:<14} nulled={raw_count:>9,}  ({share:5.2f}%)  "
                  f"nan {nan_before:,}→{nan_after:,}")
        # informational only, no assertion
        print(f"  points==100 (preserved range ceiling): {int((df['points'] == 100).sum()):,}")
