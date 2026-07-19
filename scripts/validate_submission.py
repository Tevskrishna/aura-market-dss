"""Validate submission readiness — run before demos."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

REQUIRED_PAGES = [
    "1_Market_Overview.py",
    "2_Competition_Intelligence.py",
    "3_Buyer_Analytics.py",
    "4_Marketing_Intelligence.py",
    "5_DMAIC_Workspace.py",
    "6_Builder_Deep_Dive.py",
    "7_Digital_Twin.py",
    "8_AI_Recommendations.py",
    "9_SPC_Control_Chart.py",
    "10_Map_Decision_Support.py",
    "11_Executive_Reports.py",
    "12_Forecasting.py",
]

REQUIRED_DATA = [
    "projects.csv",
    "monthly_absorption.csv",
    "buyer_demographics.csv",
    "marketing_spends.csv",
    "zones.csv",
    "rera_projects.csv",
    "upcoming_projects.csv",
    "under_construction.csv",
    "land_prices.csv",
]


def main() -> int:
    errors: list[str] = []
    pages = ROOT / "pages"
    data = ROOT / "data"
    for p in REQUIRED_PAGES:
        if not (pages / p).exists():
            errors.append(f"Missing page {p}")
    for d in REQUIRED_DATA:
        if not (data / d).exists():
            errors.append(f"Missing data {d}")

    from services.data_loader import clear_catalog_cache, load_catalog
    from services.map_service import scored_zones
    from services.report_service import build_executive_markdown

    clear_catalog_cache()
    cat = load_catalog()
    if not cat.report or not cat.report.ready_for_market_overview:
        errors.append("Catalog not ready for Market Overview")
    z = scored_zones()
    if len(z) < 20:
        errors.append("Expected ~25 scored zones")
    md = build_executive_markdown()
    if "Executive Decision Brief" not in md:
        errors.append("Executive brief generation failed")

    if errors:
        print("FAIL")
        for e in errors:
            print(" -", e)
        return 1
    print("PASS — submission pack looks complete")
    print(f" pages={len(REQUIRED_PAGES)} zones={len(z)} brief_chars={len(md)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
