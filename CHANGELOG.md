# Changelog

## [0.3.2] — 2026-06-24

### Fixed
- User-Agent for CDFI Fund downloads aligned to the portfolio identifying-token
  standard (cdfidata/<ver> (+repo) + Accept/Accept-Language), replacing a
  browser-mimic "Mozilla/5.0 (compatible; cdfidata…)" string. A browser UA over
  a python-requests TLS stack is a fingerprint mismatch that can 403 on
  RESIDENTIAL connections. NOT a cloud/403 fix — cdfifund.gov does not block
  datacenter IPs (one-time cached bulk download).

### Internal/CI
- ci.yml now runs pytest with -m "not live" so cloud runners no longer execute
  the live cdfifund.gov tests (false-red / fingerprint avoidance). release.yml's
  test-wheel job already deselected live; unchanged.

## [0.3.1] — 2026-06-04

### Fixed
- TLRLoader.summary() printed "FYNone" for a single-year load_range(Y, Y); the
  single-release header now falls back to the loaded source_release label (e.g. "FY2020").

### Internal/CI
- ci.yml actions SHA-pinned (checkout v4.3.1, setup-python v5.6.0) to match
  release.yml; test_schema_doc_matches_canonical strengthened to verify the full
  header->canonical mapping against schema.py.

## [0.3.0] — 2026-06-03

### Added
- load_cumulative() and load_range(start, end): cumulative TLR for the AMIS era (FY2020–FY2022),
  stacked with provenance, NO dedup.
- source_release and state provenance columns on all loads (output now 63 cols: 61 canonical + 2).
- docs/CANONICAL_SCHEMA.md.

### Changed — single-year load() output (affects existing load(year=...))
- Unified 61-column canonical schema across both export eras.
- naics_name → naics_code (renamed; holds 6-digit NAICS codes, not names).
- capacity_* (×5) now numeric (float).
- ACPR FY2020/FY2021 FIPS leading-zero recovery: fips_code zero-padded to 11; derived state corrected.
- Documented not-reported codes nulled to NaN, field-specifically: interest_rate 99, term_months 999,
  points 99, naics_code 999999. (points 100 left as-is — see docs/CANONICAL_SCHEMA.md.)
- summary() is now multi-release-aware (per-source_release breakdown + overlap caveat instead of a
  misleading cross-release total).

### Notes
- Releases overlap on fiscal_year — FY2022 (AMIS) restates/expands prior-year (FY2021) data;
  fiscal_year is NOT a dedup key across releases.
- Field completeness is era-dependent (rate/term/NAICS especially). Prefer filtering by source_release;
  do not naively aggregate the full cumulative frame.
- fiscal_year is the CDFI Fund "TLR Submission Year" (name kept, caveat documented).

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
