"""
Land price arbitrage + Developer Margin Viability Index (AURA-Market spec).

Business problem: launch pricing without land cost / margin grounding.
"""
from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from config import settings
from services.adapters import get_adapter


@dataclass(frozen=True)
class MarginRow:
    project: str
    developer: str
    micro_market: str
    sale_price_psf: float
    land_price_psf: float
    construction_cost_psf: float
    loaded_land_psf: float
    implied_margin_psf: float
    margin_pct: float
    viability: str


def _nearest_land(micro_market: str, land: pd.DataFrame) -> float:
    if land.empty:
        return float("nan")
    mm = str(micro_market).lower()
    for _, row in land.iterrows():
        name = str(row["micro_market"]).lower()
        if "bagaluru" in mm and "bagaluru" in name:
            return float(row["land_price_psf"])
        if name in mm or mm in name:
            return float(row["land_price_psf"])
    # default to Bagaluru row if present
    hit = land[land["micro_market"].astype(str).str.contains("Bagaluru", case=False, na=False)]
    if not hit.empty:
        return float(hit.iloc[0]["land_price_psf"])
    return float(land["land_price_psf"].median())


def _viability_label(margin_pct: float) -> str:
    if margin_pct >= settings.MARGIN_VIABLE_PCT:
        return "Viable"
    if margin_pct >= settings.MARGIN_STRESSED_PCT:
        return "Stressed"
    return "Unviable"


def build_margin_viability(
    projects: pd.DataFrame | None = None,
    land: pd.DataFrame | None = None,
    construction_cost_psf: float | None = None,
) -> pd.DataFrame:
    adapter = get_adapter()
    projects = projects if projects is not None else adapter.projects()
    land = land if land is not None else adapter.land_prices()
    build_cost = construction_cost_psf if construction_cost_psf is not None else settings.CONSTRUCTION_COST_PSF

    rows = []
    for _, p in projects.iterrows():
        land_psf = _nearest_land(p.get("micro_market", settings.MICRO_MARKET_DEFAULT), land)
        loaded_land = land_psf * settings.LAND_FSI_LOAD_FACTOR
        sale = float(p["price_psf"])
        margin_psf = sale - loaded_land - build_cost
        margin_pct = (margin_psf / sale * 100) if sale else 0.0
        rows.append(
            {
                "project": p["project"],
                "developer": p["developer"],
                "micro_market": p.get("micro_market", settings.MICRO_MARKET_DEFAULT),
                "sale_price_psf": round(sale, 0),
                "land_price_psf": round(land_psf, 0),
                "construction_cost_psf": round(build_cost, 0),
                "loaded_land_psf": round(loaded_land, 0),
                "implied_margin_psf": round(margin_psf, 0),
                "margin_pct": round(margin_pct, 1),
                "viability": _viability_label(margin_pct),
            }
        )
    return pd.DataFrame(rows).sort_values("margin_pct")


def margin_kpis(df: pd.DataFrame) -> dict:
    if df.empty:
        return {"avg_margin_pct": 0.0, "viable": 0, "stressed": 0, "unviable": 0}
    return {
        "avg_margin_pct": round(float(df["margin_pct"].mean()), 1),
        "viable": int((df["viability"] == "Viable").sum()),
        "stressed": int((df["viability"] == "Stressed").sum()),
        "unviable": int((df["viability"] == "Unviable").sum()),
    }
