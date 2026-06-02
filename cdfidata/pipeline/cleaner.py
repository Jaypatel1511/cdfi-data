"""
Standardize and clean raw CDFI Fund DataFrames.
Handles column renaming, type casting, null handling, and boolean normalization.
"""
import pandas as pd
from cdfidata.utils.schema import BOOL_TRUE_VALUES, BOOL_FALSE_VALUES


def normalize_columns(df: pd.DataFrame, column_map: dict) -> pd.DataFrame:
    """
    Rename columns using a mapping dict.
    Only renames columns that exist in the DataFrame.

    Args:
        df:         Raw DataFrame
        column_map: Dict of {RAW_NAME: clean_name}

    Returns:
        DataFrame with renamed columns
    """
    df.columns = df.columns.str.strip().str.upper()
    available = {k: v for k, v in column_map.items() if k in df.columns}
    return df.rename(columns=available)


def cast_types(df: pd.DataFrame, dtype_map: dict) -> pd.DataFrame:
    """
    Cast columns to specified types.
    Silently skips columns that don't exist or can't be cast.

    Args:
        df:        DataFrame with clean column names
        dtype_map: Dict of {column_name: type_string}

    Returns:
        DataFrame with cast columns
    """
    for col, dtype in dtype_map.items():
        if col not in df.columns:
            continue
        try:
            if dtype == "bool":
                df[col] = df[col].apply(_parse_bool)
            elif dtype == "int":
                df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")
            elif dtype == "float":
                df[col] = pd.to_numeric(df[col], errors="coerce")
            else:
                df[col] = df[col].astype(dtype)
        except Exception:
            pass
    return df


def _parse_bool(val) -> bool:
    """Parse a value to boolean using CDFI Fund conventions."""
    if pd.isna(val):
        return None
    s = str(val).strip()
    if s in BOOL_TRUE_VALUES:
        return True
    if s in BOOL_FALSE_VALUES:
        return False
    return None


def clean_strings(df: pd.DataFrame, cols: list = None) -> pd.DataFrame:
    """
    Strip whitespace and normalize string columns to uppercase.

    Args:
        df:   DataFrame
        cols: List of columns to clean (default: all object columns)

    Returns:
        Cleaned DataFrame
    """
    if cols is None:
        cols = df.select_dtypes(include="object").columns.tolist()
    for col in cols:
        if col in df.columns:
            df[col] = df[col].str.strip()
    return df


def drop_empty_rows(df: pd.DataFrame, required_cols: list) -> pd.DataFrame:
    """Drop rows where all required columns are null; raise if a required column is missing."""
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise ValueError(
            f"Required column(s) {missing} not found after standardization; "
            f"the source schema may have changed. Got columns: {list(df.columns)}"
        )
    return df.dropna(subset=required_cols, how="all")


def standardize(
    df: pd.DataFrame,
    column_map: dict,
    dtype_map: dict,
    required_cols: list = None,
) -> pd.DataFrame:
    """
    Full standardization pipeline: rename → cast → clean → drop empty.

    Args:
        df:            Raw DataFrame
        column_map:    Column rename mapping
        dtype_map:     Type casting mapping
        required_cols: Columns required to be non-null

    Returns:
        Clean, standardized DataFrame
    """
    df = normalize_columns(df, column_map)
    df = cast_types(df, dtype_map)
    df = clean_strings(df)
    if required_cols:
        df = drop_empty_rows(df, required_cols)
    df = df.reset_index(drop=True)
    return df
