# cdfidata canonical TLR schema

The canonical TLR schema is **DEFINED in code** — see `cdfidata/utils/schema.py`
(`TLR_CANONICAL`, `TLR_COLUMNS`, `ACPR_COLUMNS`, `TLR_COLUMNS_BY_YEAR`). This file
*documents* that definition; the code is the source of truth. If the two ever drift,
the code wins and this doc (and its anti-drift test) should be updated.

`load(year=...)` returns the unified **61-column canonical schema** across both export
eras, regardless of which source release a year came from:

- **AMIS** (Salesforce export) — FY2022. Headers are uppercased + truncated to 32 chars
  by the export; mapped in `TLR_COLUMNS`.
- **ACPR** — FY2020 / FY2021. Headers mapped in `ACPR_COLUMNS`.

`TLR_COLUMNS_BY_YEAR` selects the map per year: `{2020: ACPR, 2021: ACPR, 2022: AMIS}`.

Each canonical column appears in both eras **except `award_category`, which is AMIS-only**
(ACPR has no equivalent header — shown as "—" below; reindexed to NaN for FY2020/FY2021).

## Provenance columns

In addition to the 61 canonical columns, `load()` adds two provenance columns:

| Column | Meaning |
|---|---|
| `source_release` | The release a row came from, labelled `FY{year}` (e.g. `FY2020`, `FY2022`). Use this — not `fiscal_year` — to disambiguate overlapping releases. |
| `state` | Two-letter USPS state, derived from `fips_code` (FIPS state prefix). ACPR FY2020/FY2021 strip the FIPS leading zero; `fips_code` is zero-padded to 11 and `state` corrected. |

**Output is 63 columns: 61 canonical + 2 provenance (`source_release`, `state`).**

## Canonical mapping table

One row per canonical column. "AMIS source header" is the key in `TLR_COLUMNS` (FY2022);
"ACPR source header" is the key in `ACPR_COLUMNS` (FY2020/FY2021), "—" where AMIS-only.

| Canonical name | AMIS source header (FY2022) | ACPR source header (FY2020/FY2021) | Notes |
|---|---|---|---|
| org_id | ORG_ID | ORG_ID | |
| transaction_id | TRANS_ID | TRANS_ID | |
| fiscal_year | TLR_SUBMISSION_YEAR__C | FISCALYEAR | CDFI Fund "TLR Submission Year"; name kept, NOT a dedup key across releases |
| amount | ORIGINAL_LOAN_INVESTMENT_AMOUNT_ | ORIGINALAMOUNT | |
| fips_code | FIPSCODE_2010 | PROJECTFIPSCODE_2010 | ACPR strips leading zero; zero-padded to 11 in load() |
| investee_type | INVESTEE_TYPE__C | INVESTEETYPE | |
| date_originated | DATE_ORIGINATED__C | DATECLOSED | |
| purpose | PURPOSE__C | PURPOSE | |
| transaction_type | TRANSACTION_TYPE__C | TRANSACTIONTYPE | |
| interest_rate | INTEREST_RATE__C | ORIGINALINTERESTRATE | not-reported code 99 → NaN |
| interest_type | INTEREST_TYPE__C | INTERESTTYPE | |
| points | POINTS__C | POINTS | not-reported code 99 → NaN; 100 left as-is (range ceiling) |
| origination_fees | ORIGINATION_FEES__C | ORIGINATIONFEES | |
| amortization_type | AMORTIZATION_TYPE__C | AMORTIZATIONTYPE | |
| equity_like_features | EQUITY_LIKE_FEATURES__C | EQUITYLIKEFEATURES | |
| term_months | TERM_IN_MONTHS__C | ORIGINALTERM | not-reported code 999 → NaN |
| guarantee | GUARANTEE__C | GUARANTEE | |
| type_of_jobs_reported | TYPE_OF_JOBS_REPORTED__C | JOBTYPE | |
| source_of_job_estimates | SOURCE_OF_JOB_ESTIMATES__C | JOBSOURCE | |
| source_of_job_estimates_other | SOURCE_OF_JOB_ESTIMATES_OTHER__C | JOBSOURCEOTHER | |
| community_facility | COMMUNITY_FACILITY__C | COMMUNITYFACILITY | |
| desc_other_otp_end_use | DESC_OF_OTHER_APPROVED_OTP_END_U | DESCOFOTHEROTPENDUSERS | |
| forgivable_loan | FORGIVABLE_LOAN__C | FORGIVABLELOAN | |
| naics_code | NAICS_NAME | NAICSCODE | renamed from naics_name; holds 6-digit NAICS codes, not names. not-reported code 999999 → NaN |
| date_business_established | DATE_BUSINESS_ESTABLISHED__C | DATEBUSINESSESTABLISHED | |
| entity_structure | ENTITY_STRUCTURE__C | ENTITYSTRUCTURE | |
| minority_owned | MINORITY_OWNED_OR_CONTROLLED__C | MINORITYOWNEDORCONTROLLED | |
| women_owned | WOMEN_OWNED_OR_CONTROLLED__C | WOMENOWNEDORCONTROLLED | |
| description_other_approved | DESCRIPTION_OF_THE_OTHER_APPROVE | DESCOFOTHEROTP | |
| low_income_owned | LOW_INCOME_OWNED_OR_CONTROLLED__ | LOWINCOMEOWNEDORCONTROLLED | |
| low_income_status | LOW_INCOME_STATUS__C | LOWINCOMESTATUS | |
| other_targeted_populations | OTHER_TARGETED_POPULATIONS__C | OTHERTARGETEDPOPULATIONS | |
| litp_end_users | LITP_END_USERS__C | LITPENDUSERS | |
| otp_end_users | OTP_END_USERS__C | OTPENDUSERS | |
| ia_end_users | IA_END_USERS__C | IAENDUSERS | |
| gender | GENDER__C | GENDER | |
| race | RACE__C | RACE | |
| hispanic_origin | HISPANIC_ORIGIN__C | HISPANICORIGIN | |
| female_headed_household | FEMALE_HEADED_HOUSEHOLD__C | FEMALEHEADEDHOUSEHOLD | |
| first_time_home_buyer | FIRST_TIME_HOME_BUYER__C | FIRSTTIMEHOMEBUYER | |
| capacity_educational | CAPACITY_OF_EDUCATIONAL_COMMUNIT | EDUCATIONFACILITY | numeric (float) |
| capacity_childcare | CAPACITY_OF_CHILDCARE_COMMUNITY_ | CHILDCAREFACILITY | numeric (float) |
| capacity_healthcare | CAPACITY_OF_HEALTHCARE_COMMUNITY | HEALTHCAREFACILITY | numeric (float) |
| capacity_arts_center | CAPACITY_OF_ARTS_CENTER_COMMUNIT | ARTSCENTERFACILITY | numeric (float) |
| capacity_other_facility | CAPACITY_OF_OTHER_COMMUNITY_FACI | OTHERFACILITY | numeric (float) |
| sqft_total | SQUARE_FEET_OF_REAL_ESTATE_TOTAL | AREAREALESTATETOTAL | |
| sqft_manufacturing | SQUARE_FEET_OF_REAL_ESTATE_MANUF | SQFREMANUFACTURE | |
| sqft_office | SQUARE_FEET_OF_REAL_ESTATE_OFFIC | SQFREOFFICE | |
| sqft_retail | SQUARE_FEET_OF_REAL_ESTATE_RETAI | SQFRERETAIL | |
| affordable_units_sale | AFFORDABLE_HOUSING_UNITS_SALE__C | AFFORDABLEHOUSESALE | |
| affordable_units_rental | AFFORDABLE_HOUSING_UNITS_RENTAL_ | AFFORDABLEHOUSERENT | |
| loan_status | LOAN_STATUS__C | LOANCLOSEDSTATUS | |
| banked_at_intake | BANKED_AT_TIME_OF_INTAKE__C | BANKEDATTIMEOFINTAKE | |
| annual_gross_revenue | ANNUAL_GROSS_REVENUE_FROM_BUSINE | ANNUALGROSSREVENUE | |
| total_project_cost | TOTAL_PROJECT_COST__C | TOTALPROJECTCOST | |
| proj_perm_jobs_financed | PROJ_PERM_JOBS_TO_BE_CREATED_FIN | PROJECTEDJOBSBUSINESS | |
| proj_perm_jobs_tenant | PROJ_PERM_JOBS_CREATED_TENANT_BU | PROJECTEDFTETENANTS | |
| projected_jobs_construction | PROJECTED_JOBS_TO_BE_CREATED_CON | PROJECTEDJOBSCONSTRUCTION | |
| housing_units_sale | HOUSING_UNITS_SALE__C | HOUSINGUNITSSALE | |
| housing_units_rental | HOUSING_UNITS_RENTAL__C | HOUSINGUNITSRENT | |
| award_category | AWARDCATEGORY | — | AMIS-only; NaN for ACPR FY2020/FY2021 |

## Sentinel / not-reported value handling (0.3.0)

Several TLR numeric fields carry CDFI Fund "not reported / not applicable" codes (TLR Data Point
Guidance, Feb 2022). These were imported as real numbers through 0.2.0 and corrupt aggregations.
0.3.0 nulls ONLY the values the guidance documents as not-reported, field-specifically, in load()
after canonicalization (both eras + the cumulative API inherit it). Cells → NaN; no rows dropped.

### Nulled (documented not-reported codes) — validated shares
| Canonical field | Code → NaN | Guidance col | FY2022 (AMIS) | FY2020 (ACPR)* |
|---|---|---|---|---|
| interest_rate | 99 | I | 416,941 (41.59%) | 154 (0.05%) |
| term_months | 999 | O | 419,514 (41.85%) | 40 (0.01%) |
| points | 99 | K | 48,469 (4.83%) | 26,281 (9.05%) |
| naics_code | 999999 | U | 15,454 (1.54%) | 99,797 (34.36%) |

\* FY2021 (also ACPR) inherits the same field-specific nulling via load(); not separately measured.

Completeness is strongly era-dependent — the missingness is itself a function of reporting era,
not only composition. rate/term "not reported" is ~42% in AMIS vs ~0% in ACPR; NAICS-unknown is
~34% in FY2020 vs ~1.5% in FY2022. Consequence: cumulative aggregates over rate/term/NAICS are
confounded by era reporting completeness (and likely era composition). Prefer per-source_release
analysis; do not compute a single median rate / industry mix across the full frame.

### Documented but deliberately NOT nulled in 0.3.0 (left real, flagged)
| Field | Value | Why not nulled |
|---|---|---|
| points | 100 | Range ceiling (0–100), not a documented not-reported code. 100% points is implausible → flagged as likely data-quality, but undocumented; nulling would assert missingness the codebook doesn't. Confirmed negligible: 7 rows FY2022, 0 FY2020. |
| original_amount | 1 | "enter 1 if LOC credit limit unknown" — conditional on LOC transaction types, and a summed field; nulling moves totals. Revisit with transaction-type-conditional handling. |
| total_project_cost | == original_amount | "enter the loan amount if unknown" — copy-another-field, no constant; nulling on equality erases genuinely equal-cost projects. |
| date_business_established | == date_originated | "enter Date Originated if unknown" — same copy-field trap, on a date. |
| capacity_* (×5), gross_revenue | 0 | "enter 0 if unknown/NA" — 0 is also a genuine zero; nulling fabricates missingness. Aggregations treat 0 as mostly NA. |

### Confirmed real (NOT codes)
interest_rate 0/1/18 (deeply-subsidized 0–1% and consumer/usury-cap 18% rates), term_months 6
(short / LOC term; days reported as fractions). Heavy clustering is product concentration (a large
subsidized/consumer/LOC book), not a sentinel — a documentation note, not a cleansing target.

Policy: null only what the guidance documents as not-reported for that specific field; never null
on plausibility alone. Categorical fields carry their own documented missing markers ("Do Not
Know", "NA") — do not count these as substantive levels in shares.
