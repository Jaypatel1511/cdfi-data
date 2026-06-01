# cdfi-data 🏦

**ETL pipeline for US Treasury CDFI Fund public datasets.**

Download, clean, and analyze Transaction Level Report (TLR), Consumer Loan Report (CLR),
and Awards data from the US Department of Treasury's CDFI Fund — in one line of Python.

---

## Why cdfi-data?

The CDFI Fund releases massive public datasets covering millions of loans and investments
in low-income communities. But the raw files are messy, inconsistently formatted, and
require significant cleaning before analysis. cdfi-data standardizes the entire pipeline.

---

## Installation

    pip install cdfidata

---

## Quickstart

    from cdfidata import TLRLoader, CLRLoader, AwardsLoader

    # Load TLR transaction data (downloads & caches automatically)
    tlr = TLRLoader()
    df = tlr.load(year=2022)

    # Filter to Illinois
    il = tlr.filter_state("IL")

    # Filter by loan type and amount
    small_biz = tlr.filter_loan_type("Business")
    large = tlr.filter_amount(min_amount=500_000)

    # Summary stats
    tlr.summary()

    # Export
    tlr.to_csv("cdfi_transactions.csv")
    tlr.to_sqlite("cdfi.db", table="tlr")

---

## Sample Data (No Download Required)

    from cdfidata import TLRLoader, CLRLoader, AwardsLoader

    tlr = TLRLoader()
    df = tlr.load_sample(n=1000)

    clr = CLRLoader()
    df = clr.load_sample(n=1000)

    awards = AwardsLoader()
    df = awards.load_sample(n=500)

---

## Datasets Supported

| Dataset | Source | Description |
|---------|--------|-------------|
| TLR (Transaction Level Report) | CDFI Fund | 1M+ individual CDFI loans, 61 variables |
| CLR (Consumer Loan Report) | CDFI Fund | 3.2M consumer loans aggregated to census tract |
| Awards Database | CDFI Fund | All CDFI Fund program awardees across all years |

---

## Data Sources

**CDFI Fund datasets** (TLR, CLR, Awards) come from the US Department of Treasury CDFI Fund:
https://www.cdfifund.gov/research-data

All data is released under open government data principles.

---

## Running Tests

    PYTHONPATH=. pytest tests/ -v

30 tests across all modules.

---

## Who This Is For

- Impact investors analyzing CDFI loan portfolios
- Academic researchers studying community development finance
- Policy analysts evaluating CDFI Fund program outcomes
- CDFIs benchmarking their own performance against peers
- Anyone who needs clean, analysis-ready CDFI Fund data

---

## License

MIT 2026 Jaypatel1511
