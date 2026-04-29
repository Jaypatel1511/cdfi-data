"""
CDFI Fund Awards Database loader.
Covers all CDFI Fund program awardees across all years.
"""
import pandas as pd
import numpy as np
import random
from typing import Optional

from cdfidata.pipeline.cleaner import standardize
from cdfidata.pipeline.exporter import to_csv, to_sqlite
from cdfidata.utils.schema import AWARDS_COLUMNS, AWARDS_DTYPES


class AwardsLoader:
    """
    Loader for CDFI Fund Awards Database.

    Usage:
        loader = AwardsLoader()
        df = loader.load_sample()
        df_il = loader.filter_state("IL")
    """

    def __init__(self):
        self._df: Optional[pd.DataFrame] = None

    def load_from_file(self, path: str) -> pd.DataFrame:
        """Load awards data from a local CSV file."""
        print(f"Loading awards data from {path}...")
        df = pd.read_csv(path, dtype=str, low_memory=False)
        df = standardize(df, AWARDS_COLUMNS, AWARDS_DTYPES,
                         required_cols=["award_amount"])
        self._df = df
        return df

    def load_sample(self, n: int = 500) -> pd.DataFrame:
        """Generate synthetic awards sample data for testing."""
        random.seed(42)
        np.random.seed(42)

        states = ["IL", "NY", "CA", "TX", "GA", "NC", "OH", "PA", "FL", "MI"]
        programs = ["FA", "NACA", "NMTC", "BEA", "CMF", "BOND"]
        inst_types = ["Loan Fund", "Bank", "Credit Union", "Venture Fund",
                      "Depository Institution Holding Company"]

        records = []
        for i in range(n):
            records.append({
                "awardee_name": f"Community Development Fund {i+1}",
                "state": random.choice(states),
                "award_year": random.randint(2010, 2023),
                "award_amount": round(np.random.lognormal(14, 1)),
                "program": random.choice(programs),
                "award_type": "Financial Assistance",
                "institution_type": random.choice(inst_types),
            })

        self._df = pd.DataFrame(records)
        return self._df

    def filter_state(self, state: str) -> pd.DataFrame:
        self._check_loaded()
        return self._df[self._df["state"] == state.upper()].copy()

    def filter_program(self, program: str) -> pd.DataFrame:
        self._check_loaded()
        return self._df[
            self._df["program"].str.contains(program, case=False, na=False)
        ].copy()

    def filter_year(self, year: int) -> pd.DataFrame:
        self._check_loaded()
        return self._df[self._df["award_year"] == year].copy()

    def summary(self) -> None:
        self._check_loaded()
        df = self._df
        print(f"\nAwards Database Summary")
        print(f"  Total awards:     {len(df):,}")
        print(f"  Total amount:     ${df['award_amount'].sum()/1e9:.2f}B")
        print(f"  States covered:   {df['state'].nunique()}")
        print(f"  Programs:         {df['program'].nunique()}")
        print(f"  Year range:       {df['award_year'].min()}–{df['award_year'].max()}")
        print()

    def to_csv(self, path: str) -> None:
        self._check_loaded()
        to_csv(self._df, path)

    def to_sqlite(self, db_path: str, table: str = "awards") -> None:
        self._check_loaded()
        to_sqlite(self._df, db_path, table)

    def _check_loaded(self) -> None:
        if self._df is None:
            raise RuntimeError(
                "No data loaded. Call .load_from_file() or .load_sample() first."
            )
