"""
Domain models shared across Market Overview, Competition, DMAIC, Twin, Forecast.

Keep these serialization-friendly (dataclasses) so services stay UI-agnostic.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Any


@dataclass(frozen=True)
class FilterState:
    """Global decision filters applied to every MEASURE / ANALYZE view."""

    builder: str
    project: str
    date_start: date | None
    date_end: date | None
    quarter: str


@dataclass(frozen=True)
class DatasetStatus:
    name: str
    ok: bool
    rows: int
    path: str
    errors: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()


@dataclass(frozen=True)
class ValidationReport:
    datasets: tuple[DatasetStatus, ...]
    ready_for_market_overview: bool

    @property
    def errors(self) -> list[str]:
        out: list[str] = []
        for d in self.datasets:
            out.extend(f"[{d.name}] {e}" for e in d.errors)
        return out


@dataclass(frozen=True)
class MarketKPIs:
    """CTQ scorecard for DEFINE/MEASURE — Market Overview foundation."""

    total_projects: int
    total_units: int
    bookings: int
    marketing_spend_cr: float
    sales_value_cr: float
    absorption_rate_pct: float
    active_builders: int
    buyer_distribution: dict[str, int] = field(default_factory=dict)

    def as_cards(self) -> list[dict[str, Any]]:
        return [
            {"label": "Total Projects", "value": self.total_projects, "format": "int"},
            {"label": "Total Units", "value": self.total_units, "format": "int"},
            {"label": "Bookings", "value": self.bookings, "format": "int"},
            {"label": "Marketing Spend", "value": self.marketing_spend_cr, "format": "cr"},
            {"label": "Sales Value", "value": self.sales_value_cr, "format": "cr"},
            {"label": "Absorption Rate", "value": self.absorption_rate_pct, "format": "pct"},
            {"label": "Active Builders", "value": self.active_builders, "format": "int"},
            {
                "label": "Buyer Segments",
                "value": len(self.buyer_distribution),
                "format": "int",
                "help": "Distinct unit-mix segments in filtered bookings",
            },
        ]


@dataclass(frozen=True)
class MarketBundle:
    """Filtered analytical frames produced once and reused by charts + KPIs."""

    projects: Any  # pd.DataFrame — typed loosely to avoid circular pandas import at model layer
    monthly: Any
    bookings: Any
    marketing: Any
    kpis: MarketKPIs
