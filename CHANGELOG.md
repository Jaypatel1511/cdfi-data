# Changelog

## 0.2.0 — 2026-06-01

- Added: browser User-Agent on downloads (defensive against CDN configs that reject default agents).
- Fixed: FY2022 TLR URL refreshed to the current CDFI Fund media URL; removed dead FY2021 URL.
- Fixed: TLR column schema replaced with the real AMIS Salesforce headers — load(year=2022)
  now returns real data (previously raised KeyError: 'amount' on every real load).
- Added: optional url= override on load()/download_tlr(); latin-1 fallback for non-UTF-8 files.
- Added: 'state' column derived from fips_code; filter_state and summary now work on real data.
- Changed: filter_loan_type now matches transaction_type; drop_empty_rows raises a clear
  ValueError on missing required columns instead of a bare KeyError.
- Note: load_sample is still illustrative; schema reconciliation deferred to 0.2.1.

## 0.1.8

- Docs: removed phantom LCA (H-1B/OFLC) dataset claim and trimmed package description to implemented datasets (TLR, CLR, Awards). Fixed `__version__` drift (was 0.1.0). No code/behavior changes.
