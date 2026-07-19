"""
DMAIC workspace shell — DEFINE/MEASURE hooks; ANALYZE/IMPROVE expand next.

Keeps root-cause and sigma utilities reusable without bloating UI pages.
"""
from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from config import settings
from models.market import FilterState
from services.data_loader import load_catalog
from services.filter_service import apply_filters
from services.market_service import compute_kpis


@dataclass(frozen=True)
class DmaicSnapshot:
    problem_statement: str
    ctqs: list[str]
    kpis: dict
    pareto: pd.DataFrame
    at_risk: pd.DataFrame


def build_dmaic_snapshot(filters: FilterState) -> DmaicSnapshot:
    frames = apply_filters(load_catalog(), filters)
    projects = frames["projects"]
    kpis = compute_kpis(projects, frames["bookings"], frames["marketing"], frames["monthly"])

    unsold = projects.sort_values("units_unsold", ascending=False).copy()
    unsold["share_pct"] = (unsold["units_unsold"] / max(unsold["units_unsold"].sum(), 1) * 100).round(1)
    unsold["cumulative_pct"] = unsold["share_pct"].cumsum().round(1)

    at_risk = projects[projects["absorption_pct"] < settings.ABSORPTION_AT_RISK_PCT].sort_values("absorption_pct")

    return DmaicSnapshot(
        problem_statement=(
            "Reduce residential unsold inventory (defect) in Bagaluru micro-market by improving "
            "pricing, construction confidence, unit mix, and competitive positioning."
        ),
        ctqs=[
            f"Absorption ≥ {settings.ABSORPTION_HEALTHY_PCT:.0f}%",
            f"At-risk projects (<{settings.ABSORPTION_AT_RISK_PCT:.0f}%) minimised",
            "Marketing efficiency (outcome per ₹ Cr) improving QoQ",
            "Booking velocity stable within SPC limits",
        ],
        kpis={
            "absorption_pct": kpis.absorption_rate_pct,
            "unsold_units": int(projects["units_unsold"].sum()) if not projects.empty else 0,
            "at_risk_projects": int(len(at_risk)),
            "bookings": kpis.bookings,
            "marketing_spend_cr": kpis.marketing_spend_cr,
        },
        pareto=unsold[["project", "developer", "units_unsold", "share_pct", "cumulative_pct", "absorption_pct"]],
        at_risk=at_risk[
            [c for c in ["project", "developer", "absorption_pct", "price_psf", "construction_delay_months", "units_unsold"] if c in at_risk.columns]
        ],
    )
