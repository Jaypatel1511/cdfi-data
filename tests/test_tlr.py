import pytest
import pandas as pd
from cdfidata.sources.tlr import TLRLoader
from cdfidata.pipeline import downloader


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
