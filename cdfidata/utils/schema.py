"""
Column mappings, data dictionaries, and constants for CDFI Fund public datasets.
All source URLs and field definitions are based on official CDFI Fund documentation.
"""

# ── TLR (Transaction Level Report) ───────────────────────────────────────────
# Source: cdfifund.gov — annual release, 61 variables, 1M+ loan observations
# Masked to protect individual CDFI identity

# Keys are the real source headers from the AMIS Salesforce export, uppercased and
# truncated to 32 chars by the source export (FY2022 live file).
TLR_COLUMNS = {
    "ORG_ID": "org_id",
    "TRANS_ID": "transaction_id",
    "TLR_SUBMISSION_YEAR__C": "fiscal_year",
    "ORIGINAL_LOAN_INVESTMENT_AMOUNT_": "amount",
    "FIPSCODE_2010": "fips_code",
    "INVESTEE_TYPE__C": "investee_type",
    "DATE_ORIGINATED__C": "date_originated",
    "PURPOSE__C": "purpose",
    "TRANSACTION_TYPE__C": "transaction_type",
    "INTEREST_RATE__C": "interest_rate",
    "INTEREST_TYPE__C": "interest_type",
    "POINTS__C": "points",
    "ORIGINATION_FEES__C": "origination_fees",
    "AMORTIZATION_TYPE__C": "amortization_type",
    "EQUITY_LIKE_FEATURES__C": "equity_like_features",
    "TERM_IN_MONTHS__C": "term_months",
    "GUARANTEE__C": "guarantee",
    "TYPE_OF_JOBS_REPORTED__C": "type_of_jobs_reported",
    "SOURCE_OF_JOB_ESTIMATES__C": "source_of_job_estimates",
    "SOURCE_OF_JOB_ESTIMATES_OTHER__C": "source_of_job_estimates_other",
    "COMMUNITY_FACILITY__C": "community_facility",
    "DESC_OF_OTHER_APPROVED_OTP_END_U": "desc_other_otp_end_use",
    "FORGIVABLE_LOAN__C": "forgivable_loan",
    "NAICS_NAME": "naics_name",
    "DATE_BUSINESS_ESTABLISHED__C": "date_business_established",
    "ENTITY_STRUCTURE__C": "entity_structure",
    "MINORITY_OWNED_OR_CONTROLLED__C": "minority_owned",
    "WOMEN_OWNED_OR_CONTROLLED__C": "women_owned",
    "DESCRIPTION_OF_THE_OTHER_APPROVE": "description_other_approved",
    "LOW_INCOME_OWNED_OR_CONTROLLED__": "low_income_owned",
    "LOW_INCOME_STATUS__C": "low_income_status",
    "OTHER_TARGETED_POPULATIONS__C": "other_targeted_populations",
    "LITP_END_USERS__C": "litp_end_users",
    "OTP_END_USERS__C": "otp_end_users",
    "IA_END_USERS__C": "ia_end_users",
    "GENDER__C": "gender",
    "RACE__C": "race",
    "HISPANIC_ORIGIN__C": "hispanic_origin",
    "FEMALE_HEADED_HOUSEHOLD__C": "female_headed_household",
    "FIRST_TIME_HOME_BUYER__C": "first_time_home_buyer",
    "CAPACITY_OF_EDUCATIONAL_COMMUNIT": "capacity_educational",
    "CAPACITY_OF_CHILDCARE_COMMUNITY_": "capacity_childcare",
    "CAPACITY_OF_HEALTHCARE_COMMUNITY": "capacity_healthcare",
    "CAPACITY_OF_ARTS_CENTER_COMMUNIT": "capacity_arts_center",
    "CAPACITY_OF_OTHER_COMMUNITY_FACI": "capacity_other_facility",
    "SQUARE_FEET_OF_REAL_ESTATE_TOTAL": "sqft_total",
    "SQUARE_FEET_OF_REAL_ESTATE_MANUF": "sqft_manufacturing",
    "SQUARE_FEET_OF_REAL_ESTATE_OFFIC": "sqft_office",
    "SQUARE_FEET_OF_REAL_ESTATE_RETAI": "sqft_retail",
    "AFFORDABLE_HOUSING_UNITS_SALE__C": "affordable_units_sale",
    "AFFORDABLE_HOUSING_UNITS_RENTAL_": "affordable_units_rental",
    "LOAN_STATUS__C": "loan_status",
    "BANKED_AT_TIME_OF_INTAKE__C": "banked_at_intake",
    "ANNUAL_GROSS_REVENUE_FROM_BUSINE": "annual_gross_revenue",
    "TOTAL_PROJECT_COST__C": "total_project_cost",
    "PROJ_PERM_JOBS_TO_BE_CREATED_FIN": "proj_perm_jobs_financed",
    "PROJ_PERM_JOBS_CREATED_TENANT_BU": "proj_perm_jobs_tenant",
    "PROJECTED_JOBS_TO_BE_CREATED_CON": "projected_jobs_construction",
    "HOUSING_UNITS_SALE__C": "housing_units_sale",
    "HOUSING_UNITS_RENTAL__C": "housing_units_rental",
    "AWARDCATEGORY": "award_category",
}

# fips_code is intentionally NOT cast, to preserve leading zeros; demographics stay
# categorical strings, not bools.
TLR_DTYPES = {
    "fiscal_year": "int",
    "amount": "float",
    "interest_rate": "float",
    "points": "float",
    "origination_fees": "float",
    "term_months": "float",
    "total_project_cost": "float",
    "annual_gross_revenue": "float",
    "sqft_total": "float",
    "sqft_manufacturing": "float",
    "sqft_office": "float",
    "sqft_retail": "float",
    "affordable_units_sale": "float",
    "affordable_units_rental": "float",
    "housing_units_sale": "float",
    "housing_units_rental": "float",
    "proj_perm_jobs_financed": "float",
    "proj_perm_jobs_tenant": "float",
    "projected_jobs_construction": "float",
}

# ── CLR (Consumer Loan Report) ────────────────────────────────────────────────
# Source: cdfifund.gov — aggregated to census tract, 12 variables

CLR_COLUMNS = {
    "FISCAL_YEAR":          "fiscal_year",
    "STATE":                "state",
    "CENSUS_TRACT":         "census_tract",
    "LOAN_TYPE":            "loan_type",
    "NUMBER_OF_LOANS":      "number_of_loans",
    "TOTAL_AMOUNT":         "total_amount",
    "AVERAGE_AMOUNT":       "average_amount",
    "LOW_INCOME_AREA":      "low_income_area",
    "MINORITY_AREA":        "minority_area",
    "RURAL_AREA":           "rural_area",
    "PROGRAM":              "program",
    "AWARD_TYPE":           "award_type",
}

CLR_DTYPES = {
    "fiscal_year":      "int",
    "number_of_loans":  "int",
    "total_amount":     "float",
    "average_amount":   "float",
    "low_income_area":  "bool",
    "minority_area":    "bool",
    "rural_area":       "bool",
}

# ── ILR (Institution Level Report) ───────────────────────────────────────────
# Source: data.gov CIIS — 11 years (FY2003-2013), 728 CDFIs

ILR_COLUMNS = {
    "FISCAL_YEAR":              "fiscal_year",
    "CDFI_NAME":                "cdfi_name",
    "STATE":                    "state",
    "INSTITUTION_TYPE":         "institution_type",
    "TOTAL_ASSETS":             "total_assets",
    "TOTAL_NET_ASSETS":         "total_net_assets",
    "TOTAL_LOANS":              "total_loans",
    "TOTAL_DEPOSITS":           "total_deposits",
    "NET_INCOME":               "net_income",
    "TOTAL_FINANCING":          "total_financing",
    "TARGET_MARKET":            "target_market",
    "CERTIFICATION_STATUS":     "certification_status",
}

ILR_DTYPES = {
    "fiscal_year":      "int",
    "total_assets":     "float",
    "total_net_assets": "float",
    "total_loans":      "float",
    "total_deposits":   "float",
    "net_income":       "float",
    "total_financing":  "float",
}

# ── NMTC Allocatee Data ───────────────────────────────────────────────────────
# Source: cdfifund.gov NMTC program allocatee database

NMTC_COLUMNS = {
    "CDE_NAME":             "cde_name",
    "STATE":                "state",
    "ALLOCATION_YEAR":      "allocation_year",
    "ALLOCATION_AMOUNT":    "allocation_amount",
    "CUMULATIVE_ALLOCATION": "cumulative_allocation",
    "SERVICE_AREA":         "service_area",
    "MISSION_FOCUS":        "mission_focus",
}

NMTC_DTYPES = {
    "allocation_year":       "int",
    "allocation_amount":     "float",
    "cumulative_allocation": "float",
}

# ── Awards Database ───────────────────────────────────────────────────────────
# Source: cdfifund.gov Awards Database

AWARDS_COLUMNS = {
    "AWARDEE_NAME":     "awardee_name",
    "STATE":            "state",
    "AWARD_YEAR":       "award_year",
    "AWARD_AMOUNT":     "award_amount",
    "PROGRAM":          "program",
    "AWARD_TYPE":       "award_type",
    "INSTITUTION_TYPE": "institution_type",
}

AWARDS_DTYPES = {
    "award_year":   "int",
    "award_amount": "float",
}

# ── Download URLs ─────────────────────────────────────────────────────────────
CDFI_FUND_BASE = "https://www.cdfifund.gov"

TLR_URLS = {
    2022: "https://www.cdfifund.gov/media/8016726/download?inline",
}

ILR_URL = "https://data.gov/dataset/data-on-cdfi-program-awardees"

NMTC_URL = "https://www.cdfifund.gov/programs-training/programs/new-markets-tax-credit/allocatees"

# ── Cache directory ───────────────────────────────────────────────────────────
import os
CACHE_DIR = os.path.join(os.path.expanduser("~"), ".cdfidata", "cache")

# ── Boolean value mappings ────────────────────────────────────────────────────
BOOL_TRUE_VALUES  = {"Y", "YES", "1", "TRUE", "X", "yes", "true", "y"}
BOOL_FALSE_VALUES = {"N", "NO",  "0", "FALSE", "",  "no",  "false", "n"}

# ── US State abbreviations ────────────────────────────────────────────────────
US_STATES = {
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
    "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
    "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
    "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
    "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY",
    "DC", "GU", "PR", "VI",
}

# ── State FIPS prefix → abbreviation ──────────────────────────────────────────
STATE_FIPS = {
    "01": "AL", "02": "AK", "04": "AZ", "05": "AR", "06": "CA", "08": "CO",
    "09": "CT", "10": "DE", "11": "DC", "12": "FL", "13": "GA", "15": "HI",
    "16": "ID", "17": "IL", "18": "IN", "19": "IA", "20": "KS", "21": "KY",
    "22": "LA", "23": "ME", "24": "MD", "25": "MA", "26": "MI", "27": "MN",
    "28": "MS", "29": "MO", "30": "MT", "31": "NE", "32": "NV", "33": "NH",
    "34": "NJ", "35": "NM", "36": "NY", "37": "NC", "38": "ND", "39": "OH",
    "40": "OK", "41": "OR", "42": "PA", "44": "RI", "45": "SC", "46": "SD",
    "47": "TN", "48": "TX", "49": "UT", "50": "VT", "51": "VA", "53": "WA",
    "54": "WV", "55": "WI", "56": "WY", "60": "AS", "66": "GU", "69": "MP",
    "72": "PR", "78": "VI",
}
