import pytest
import pandas as pd
from cdfidata.sources.clr import CLRLoader


def test_load_sample_returns_dataframe():
    loader = CLRLoader()
    df = loader.load_sample(n=100)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 100


def test_load_sample_has_required_columns():
    loader = CLRLoader()
    df = loader.load_sample(n=100)
    required = ["fiscal_year", "state", "number_of_loans", "total_amount"]
    for col in required:
        assert col in df.columns


def test_filter_state(clr_loader):
    df = clr_loader.filter_state("IL")
    assert all(df["state"] == "IL")


def test_summary_runs(clr_loader):
    clr_loader.summary()


def test_not_loaded_raises():
    loader = CLRLoader()
    with pytest.raises(RuntimeError, match="No data loaded"):
        loader.filter_state("IL")
