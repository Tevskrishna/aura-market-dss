"""Marketing Intelligence — MEASURE SMC spend efficiency."""
from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from models.market import FilterState
from services.data_loader import load_catalog
from services.filter_service import apply_filters
from services.market_service import marketing_efficiency_frame


@dataclass(frozen=True)
class MarketingInsights:
    total_spend_cr: float
    by_quarter: pd.DataFrame
    by_project: pd.DataFrame
    efficiency: pd.DataFrame


def build_marketing_insights(filters: FilterState) -> MarketingInsights:
    frames = apply_filters(load_catalog(), filters)
    marketing = frames["marketing"]
    bookings = frames["bookings"]
    projects = frames["projects"]

    if marketing.empty:
        empty = pd.DataFrame()
        return MarketingInsights(0.0, empty, empty, empty)

    by_q = marketing.groupby("fy_quarter", as_index=False)["spend_cr"].sum().sort_values("fy_quarter")
    by_p = marketing.groupby("project", as_index=False)["spend_cr"].sum().sort_values("spend_cr", ascending=False)
    eff = marketing_efficiency_frame(marketing, bookings, projects)
    return MarketingInsights(
        total_spend_cr=round(float(marketing["spend_cr"].sum()), 2),
        by_quarter=by_q,
        by_project=by_p,
        efficiency=eff,
    )
