import pytest
import pandas as pd
from cdfidata.pipeline.cleaner import (
    normalize_columns, cast_types, clean_strings,
    drop_empty_rows, standardize
)


def test_normalize_columns():
    df = pd.DataFrame({"AMOUNT": [1, 2], "STATE": ["IL", "NY"]})
    col_map = {"AMOUNT": "amount", "STATE": "state"}
    result = normalize_columns(df, col_map)
    assert "amount" in result.columns
    assert "state" in result.columns


def test_cast_types_float():
    df = pd.DataFrame({"amount": ["1000.50", "2000.00", "abc"]})
    result = cast_types(df, {"amount": "float"})
    assert result["amount"].dtype == float
    assert pd.isna(result["amount"].iloc[2])


def test_cast_types_bool():
    df = pd.DataFrame({"flag": ["Y", "N", "YES", "NO", "1", "0"]})
    result = cast_types(df, {"flag": "bool"})
    assert result["flag"].iloc[0] == True
    assert result["flag"].iloc[1] == False


def test_clean_strings():
    df = pd.DataFrame({"name": ["  IL  ", "  NY  "]})
    result = clean_strings(df)
    assert result["name"].iloc[0] == "IL"


def test_drop_empty_rows():
    df = pd.DataFrame({"amount": [100, None, 200], "state": ["IL", "NY", None]})
    result = drop_empty_rows(df, required_cols=["amount"])
    assert len(result) == 2


def test_standardize_pipeline():
    df = pd.DataFrame({
        "AMOUNT": ["1000", "2000", None],
        "STATE": [" IL ", " NY ", " CA "],
    })
    result = standardize(
        df,
        column_map={"AMOUNT": "amount", "STATE": "state"},
        dtype_map={"amount": "float"},
        required_cols=["amount"],
    )
    assert "amount" in result.columns
    assert "state" in result.columns
    assert len(result) == 2
