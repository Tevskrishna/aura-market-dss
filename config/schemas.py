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
    "micromarket_summary": [
        "micro_market",
        "projects",
        "total_units",
        "units_sold",
        "units_unsold",
        "absorption_pct",
    ],
    "inventory_trend": ["month", "absorbed_units", "unsold_units", "inventory_overhang_months"],
    "weighted_price_trend": ["period", "wt_avg_absorbed_psf", "wt_avg_available_psf"],
    "new_launches": ["month", "units_launched"],
    "productwise_supply": ["month"],
    "productwise_supply_absorption": ["month", "product_type"],
    "cumulative_supply_absorption": ["month", "cumulative_supply", "cumulative_absorption"],
    "absorption_by_price_band": ["period", "price_band", "units"],
    "micromarket_quarterly_unsold": ["region", "period", "unsold_units"],
    "micromarket_wt_price_quarterly": ["region", "period", "wt_avg_psf"],
}

# Non-blocking: loader still succeeds; warnings surface on Home / Market Overview
OPTIONAL_DATASETS = (
    "marketing_spend_share",
    "lead_insights",
    "micromarket_summary",
    "inventory_trend",
    "weighted_price_trend",
    "new_launches",
    "productwise_supply",
    "productwise_supply_absorption",
    "cumulative_supply_absorption",
    "absorption_by_price_band",
    "micromarket_quarterly_unsold",
    "micromarket_wt_price_quarterly",
)
