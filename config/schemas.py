"""
Dataset schema contracts used by the validator.

Future modules (Competition, DMAIC, Buyer Analytics) extend REQUIRED_COLUMNS
here — never redefine schemas inside pages.
"""
from __future__ import annotations

REQUIRED_COLUMNS: dict[str, list[str]] = {
    "projects": [
        "developer",
        "project",
        "total_units",
        "units_sold",
        "units_unsold",
        "price_psf",
        "avg_unit_size_sqft",
        "absorption_pct",
        "status",
    ],
    "monthly_absorption": [
        "month",
        "developer",
        "project",
        "units_sold_month",
        "cumulative_sold",
        "total_units",
        "absorption_pct",
    ],
    "buyer_demographics": [
        "source_project",
        "Created Date",
        "Primary Source",
        "Apartment Sub Type",
    ],
    "marketing_spends": [
        "project",
        "fy_label",
        "quarter",
        "period_start",
        "spend_cr",
    ],
    "zones": ["zone", "lat", "lon", "avg_price_psf"],
    "rera_projects": ["rera_id", "project", "developer", "approval_date", "units"],
    "upcoming_projects": ["project", "developer", "stage", "planned_units"],
    "under_construction": ["project", "developer", "total_units", "unsold_units"],
    "land_prices": ["micro_market", "land_price_psf"],
    "lead_insights": ["channel_cluster", "funnel_role", "indicative_share_pct", "decision_note"],
}

# Non-blocking: loader still succeeds; warnings surface on Home / Market Overview
OPTIONAL_DATASETS = ("marketing_spend_share", "lead_insights")
