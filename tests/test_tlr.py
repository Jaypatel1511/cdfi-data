import pytest
import pandas as pd
from cdfidata.sources.tlr import TLRLoader


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
