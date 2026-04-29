import pytest
import pandas as pd
from cdfidata.sources.awards import AwardsLoader


def test_load_sample_returns_dataframe():
    loader = AwardsLoader()
    df = loader.load_sample(n=100)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 100


def test_load_sample_has_required_columns():
    loader = AwardsLoader()
    df = loader.load_sample(n=100)
    required = ["awardee_name", "state", "award_year", "award_amount", "program"]
    for col in required:
        assert col in df.columns


def test_filter_state(awards_loader):
    df = awards_loader.filter_state("IL")
    assert all(df["state"] == "IL")


def test_filter_program(awards_loader):
    df = awards_loader.filter_program("FA")
    assert all(df["program"].str.contains("FA", case=False))


def test_filter_year(awards_loader):
    df = awards_loader.filter_year(2020)
    assert all(df["award_year"] == 2020)


def test_summary_runs(awards_loader):
    awards_loader.summary()


def test_not_loaded_raises():
    loader = AwardsLoader()
    with pytest.raises(RuntimeError, match="No data loaded"):
        loader.filter_state("IL")


def test_to_csv(awards_loader, tmp_path):
    path = str(tmp_path / "awards.csv")
    awards_loader.to_csv(path)
    df = pd.read_csv(path)
    assert len(df) == 200
