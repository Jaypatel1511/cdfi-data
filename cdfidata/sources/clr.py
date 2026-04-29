"""
CLR (Consumer Loan Report) data loader.
Aggregated to census tract level, 12 variables.
"""
import pandas as pd
import numpy as np
import random
from typing import Optional

from cdfidata.pipeline.cleaner import standardize
from cdfidata.pipeline.exporter import to_csv, to_sqlite, to_parquet
from cdfidata.utils.schema import CLR_COLUMNS, CLR_DTYPES


class CLRLoader:
    """
    Loader for CDFI Fund Consumer Loan Report (CLR) data.

    Usage:
        loader = CLRLoader()
        df = loader.load_sample()
        df_il = loader.filter_state("IL")
    """

    def __init__(self):
        self._df: Optional[pd.DataFrame] = None
        self._year: Optional[int] = None

    def load_from_file(self, path: str, year: int = 2022) -> pd.DataFrame:
        """
        Load CLR data from a local CSV file.

        Args:
            path: Path to the CLR CSV file
            year: Fiscal year for reference

        Returns:
            Clean pandas DataFrame
        """
        self._year = year
        print(f"Loading CLR data from {path}...")
        df = pd.read_csv(path, dtype=str, low_memory=False)
        print(f"Raw records: {len(df):,}")
        df = standardize(df, CLR_COLUMNS, CLR_DTYPES,
                         required_cols=["total_amount"])
        print(f"Clean records: {len(df):,}")
        self._df = df
        return df

    def load_sample(self, n: int = 1000) -> pd.DataFrame:
        """Generate synthetic CLR sample data for testing."""
        random.seed(42)
        np.random.seed(42)

        states = ["IL", "NY", "CA", "TX", "GA", "NC", "OH", "PA", "FL", "MI"]
        loan_types = ["Auto Loan", "Personal Loan", "Credit Card",
                      "Student Loan", "Home Improvement"]

        records = []
        for i in range(n):
            n_loans = random.randint(1, 500)
            avg = round(np.random.lognormal(8, 1))
            records.append({
                "fiscal_year": random.choice([2020, 2021, 2022]),
                "state": random.choice(states),
                "census_tract": f"{random.randint(1000, 9999):04d}",
                "loan_type": random.choice(loan_types),
                "number_of_loans": n_loans,
                "total_amount": n_loans * avg,
                "average_amount": avg,
                "low_income_area": random.choice([True, False]),
                "minority_area": random.choice([True, False]),
                "rural_area": random.choice([True, False]),
                "program": random.choice(["FA", "NACA", "RRP"]),
                "award_type": "Financial Assistance",
            })

        self._df = pd.DataFrame(records)
        return self._df

    def filter_state(self, state: str) -> pd.DataFrame:
        self._check_loaded()
        return self._df[self._df["state"] == state.upper()].copy()

    def summary(self) -> None:
        self._check_loaded()
        df = self._df
        print(f"\nCLR Data Summary")
        print(f"  Total records:    {len(df):,}")
        print(f"  Total loans:      {df['number_of_loans'].sum():,.0f}")
        print(f"  Total amount:     ${df['total_amount'].sum()/1e9:.2f}B")
        print(f"  States covered:   {df['state'].nunique()}")
        print()

    def to_csv(self, path: str) -> None:
        self._check_loaded()
        to_csv(self._df, path)

    def to_sqlite(self, db_path: str, table: str = "clr") -> None:
        self._check_loaded()
        to_sqlite(self._df, db_path, table)

    def _check_loaded(self) -> None:
        if self._df is None:
            raise RuntimeError(
                "No data loaded. Call .load_from_file() or .load_sample() first."
            )
