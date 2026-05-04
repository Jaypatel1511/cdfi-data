"""
Column mappings, data dictionaries, and constants for CDFI Fund public datasets.
All source URLs and field definitions are based on official CDFI Fund documentation.
"""

# ── TLR (Transaction Level Report) ───────────────────────────────────────────
# Source: cdfifund.gov — annual release, 61 variables, 1M+ loan observations
# Masked to protect individual CDFI identity

TLR_COLUMNS = {
    "FISCAL_YEAR":              "fiscal_year",
    "AWARD_NUMBER":             "award_number",
    "AWARDEE_TYPE":             "awardee_type",
    "FINANCING_TYPE":           "financing_type",
    "LOAN_TYPE":                "loan_type",
    "ACTIVITY_TYPE":            "activity_type",
    "AMOUNT":                   "amount",
    "TERM":                     "term_months",
    "INTEREST_RATE":            "interest_rate",
    "PURPOSE":                  "purpose",
    "STATE":                    "state",
    "CENSUS_TRACT":             "census_tract",
    "COUNTY":                   "county",
    "METROPOLITAN_AREA":        "metropolitan_area",
    "LOW_INCOME_AREA":          "low_income_area",
    "DISTRESSED_AREA":          "distressed_area",
    "MINORITY_BORROWER":        "minority_borrower",
    "WOMEN_BORROWER":           "women_borrower",
    "LOW_INCOME_BORROWER":      "low_income_borrower",
    "FIRST_TIME_BORROWER":      "first_time_borrower",
    "JOBS_CREATED":             "jobs_created",
    "JOBS_RETAINED":            "jobs_retained",
    "AFFORDABLE_UNITS":         "affordable_units",
    "PROGRAM":                  "program",
}

TLR_DTYPES = {
    "fiscal_year":          "int",
    "amount":               "float",
    "term_months":          "float",
    "interest_rate":        "float",
    "jobs_created":         "float",
    "jobs_retained":        "float",
    "affordable_units":     "float",
    "low_income_area":      "bool",
    "distressed_area":      "bool",
    "minority_borrower":    "bool",
    "women_borrower":       "bool",
    "low_income_borrower":  "bool",
    "first_time_borrower":  "bool",
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
    2022: "https://www.cdfifund.gov/sites/cdfi/files/2024-12/FY2022_TLR_CLR_Public_Data_File.zip",
    2021: "https://www.cdfifund.gov/sites/cdfi/files/2023-09/FY2021_TLR_CLR_Public_Data_File.zip",
}

ILR_URL = "https://data.gov/dataset/data-on-cdfi-program-awardees"

NMTC_URL = "https://www.cdfifund.gov/programs-training/programs/new-markets-tax-credit/allocatees"

LCA_URLS = {
    2024: "https://www.cdfifund.gov/sites/cdfi/files/2025-01/LCA_Disclosure_Data_FY2024_Q4.xlsx",
    2025: "https://www.cdfifund.gov/sites/cdfi/files/2025-03/LCA_Disclosure_Data_FY2025_Q2.xlsx",
}

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
