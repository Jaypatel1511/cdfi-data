# Changelog

All notable changes to this project will be documented in this file.

## [0.1.6] — 2026-05-04

### Changed
- Version bump

## [0.1.5] — 2026-05-04

### Added
- `CHANGELOG.md`

## [0.1.4] — 2026-05-04

### Changed
- Updated `pyproject.toml` description to explicitly mention LCA (Labor Condition Application) data

## [0.1.3] — 2026-05-04

### Fixed
- Corrected LCA download URLs from `cdfifund.gov` to the correct host: `dol.gov/agencies/eta/foreign-labor/performance`
- LCA data is published by the US Department of Labor OFLC, not the CDFI Fund

### Changed
- Updated README to distinguish CDFI Fund datasets (TLR, CLR, Awards) from DOL datasets (LCA) with source links for each

## [0.1.2] — 2026-05-03

### Added
- `LCA_URLS` dictionary in `schema.py` with entries for FY2024 Q4 and FY2025 Q2
- LCA (Labor Condition Application) data sourced from DOL OFLC quarterly disclosure files

### Fixed
- FY2024 LCA filename corrected from `LCA_Disclosure_Data_FY2024.xlsx` to `LCA_Disclosure_Data_FY2024_Q4.xlsx`

## [0.1.1] — 2026-05-03

### Fixed
- Corrected `readme` path in `pyproject.toml`
- Fixed PyPI install command in README (`pip install cdfidata`)

## [0.1.0] — 2026-05-03

### Added
- Initial release
- `TLRLoader` — Transaction Level Report pipeline (1M+ CDFI loans, 61 variables)
- `CLRLoader` — Consumer Loan Report pipeline (aggregated to census tract)
- `AwardsLoader` — CDFI Fund Awards database pipeline
- Column normalisation, dtype casting, boolean mapping via `schema.py`
- CSV and SQLite export
- Built-in sample data (no download required for testing)
- 30-test pytest suite
