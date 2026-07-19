"""
Competition Intelligence — mentor's 4 asks.

Business problem: competition blind spot before launch.
DMAIC: MEASURE supply-side context for DEFINE decisions.
"""
from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from services.adapters import DataAdapter, get_adapter


@dataclass(frozen=True)
class CompetitionSnapshot:
    rera_count: int
    upcoming_count: int
    uc_projects: int
    unsold_uc_units: int
    avg_land_psf: float
    rera: pd.DataFrame
    upcoming: pd.DataFrame
    under_construction: pd.DataFrame
    land: pd.DataFrame
    adapter_mode: str
    adapter_note: str


def build_competition_snapshot(adapter: DataAdapter | None = None) -> CompetitionSnapshot:
    adapter = adapter or get_adapter()
    rera = adapter.rera()
    upcoming = adapter.upcoming()
    under = adapter.under_construction()
    land = adapter.land_prices()
    meta = adapter.meta()
    return CompetitionSnapshot(
        rera_count=len(rera),
        upcoming_count=len(upcoming),
        uc_projects=len(under),
        unsold_uc_units=int(under["unsold_units"].sum()) if not under.empty else 0,
        avg_land_psf=float(land["land_price_psf"].mean()) if not land.empty else 0.0,
        rera=rera,
        upcoming=upcoming,
        under_construction=under,
        land=land,
        adapter_mode=meta.mode,
        adapter_note=meta.description,
    )


def launch_price_pressure(upcoming: pd.DataFrame, my_price_psf: float) -> pd.DataFrame:
    if upcoming.empty:
        return upcoming
    out = upcoming.copy()
    out["price_gap_psf"] = out["indicative_price_psf"] - my_price_psf
    out["threat"] = out["indicative_price_psf"].apply(
        lambda p: "High" if p <= my_price_psf * 1.05 else ("Medium" if p <= my_price_psf * 1.15 else "Lower")
    )
    return out.sort_values("indicative_price_psf")
