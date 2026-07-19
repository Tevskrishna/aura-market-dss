"""
AURA-Market application configuration — single source of truth.
"""
from __future__ import annotations

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
ASSETS_DIR = PROJECT_ROOT / "assets"
SQLITE_PATH = PROJECT_ROOT / "data" / "aura_catalog.sqlite"

# --- Product (Proposed Project Spec rebrand) ---
APP_TITLE = "AURA-Market: AI-Powered Predictive & Prescriptive Decision Support System for Urban Real Estate Analytics"
APP_SHORT_NAME = "AURA-Market"
PRODUCT_TAGLINE = "Launch Decision Co-pilot — GO / HOLD / NO-GO for Bagaluru pricing"
MICRO_MARKET_DEFAULT = "Bagaluru / Aerospace Highway"
PAGE_ICON = "🏙️"
COMPANY_NAME = "AURA-Market"
BRAND_MARK = "AM"

DATASETS = {
    "projects": "projects.csv",
    "monthly_absorption": "monthly_absorption.csv",
    "buyer_demographics": "buyer_demographics.csv",
    "marketing_spends": "marketing_spends.csv",
    "marketing_spend_share": "smc_spends.csv",
    "zones": "zones.csv",
    "rera_projects": "rera_projects.csv",
    "upcoming_projects": "upcoming_projects.csv",
    "under_construction": "under_construction.csv",
    "land_prices": "land_prices.csv",
    "lead_insights": "lead_insights.csv",
}

BOOKING_PROJECT_DEVELOPER = {
    "Atmosphere": "Puravankara",
    "Blubelle": "Puravankara",
    "Ecopolitan": "Puravankara",
}

MARKETING_PROJECT_ALIASES = {
    "Ecopolitan": "Ecopolitan",
    "Park Square": "Park Square",
    "Sunworth": "Sunworth",
    "Winworth": "Winworth",
    "Neora": "Neora",
    "Capella": "Capella",
    "Botanico": "Botanico",
    "Adora": "Adora De Goa",
    "Deansgate": "Deansgate",
}

# CTQs
ABSORPTION_AT_RISK_PCT = 70.0
ABSORPTION_HEALTHY_PCT = 95.0
PRICE_HIGH_PSF = 9500
CONSTRUCTION_DELAY_RISK_MONTHS = 6

# Margin viability assumptions (₹/sqft) — tunable for scenario analysis
CONSTRUCTION_COST_PSF = 3200.0
LAND_FSI_LOAD_FACTOR = 1.35  # land cost loaded into saleable area
MARGIN_VIABLE_PCT = 22.0
MARGIN_STRESSED_PCT = 12.0

# Cannibalization defaults
CANNIBAL_BUDGET_DIVERT_PCT = 0.45  # share of budget demand diverted to cheaper rival
CANNIBAL_NORMAL_DIVERT_PCT = 0.18

FY_START_MONTH = 4

KPI_COLUMNS = 4
CHART_HEIGHT = 380
DATE_FORMAT = "%Y-%m-%d"
QUARTER_LABEL_FMT = "FY {fy}-Q{q}"

ALL_BUILDERS_LABEL = "All Builders"
ALL_PROJECTS_LABEL = "All Projects"
ALL_QUARTERS_LABEL = "All Quarters"

DATA_ADAPTER_MODE = os.getenv("AURA_DATA_ADAPTER_MODE", "hybrid").lower()  # local | live | hybrid
DATA_BACKEND = os.getenv("AURA_DATA_BACKEND", "csv").lower()  # csv | sqlite
DEMO_NOTICE = "AURA-Market · hybrid adapters (live URLs when set, else validated seed CSVs)"

# Live / partner JSON endpoints (optional — enterprise path)
LIVE_RERA_URL = os.getenv("AURA_LIVE_RERA_URL", "").strip()
LIVE_UPCOMING_URL = os.getenv("AURA_LIVE_UPCOMING_URL", "").strip()
LIVE_UC_URL = os.getenv("AURA_LIVE_UC_URL", "").strip()
LIVE_LAND_URL = os.getenv("AURA_LIVE_LAND_URL", "").strip()
LIVE_TIMEOUT_SEC = float(os.getenv("AURA_LIVE_TIMEOUT_SEC", "8"))

# Auth — override demo passwords via env; optional salt enables SHA-256 hashes
AUTH_SALT = os.getenv("AURA_AUTH_SALT", "").strip()
AUTH_ADMIN_PASSWORD = os.getenv("AURA_ADMIN_PASSWORD", "admin123")
AUTH_DEMO_PASSWORD = os.getenv("AURA_DEMO_PASSWORD", "demo123")
AUTH_ADMIN_PASSWORD_HASH = os.getenv("AURA_ADMIN_PASSWORD_HASH", "").strip()
AUTH_DEMO_PASSWORD_HASH = os.getenv("AURA_DEMO_PASSWORD_HASH", "").strip()

# Karnataka / Bengaluru native city tokens for audience segmentation
NATIVE_CITY_TOKENS = (
    "bangalore",
    "bengaluru",
    "banglore",
    "banglaore",
    "bangaluru",
    "mysore",
    "mysuru",
    "hubli",
    "mangalore",
    "mangaluru",
)
