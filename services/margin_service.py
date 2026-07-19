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


@dataclass(frozen=True)
class LandDecision:
    """Should we buy / diligence this micro-market land at planned exit price?"""

    micro_market: str
    land_price_psf: float
    assumed_sale_psf: float
    construction_cost_psf: float
    loaded_land_psf: float
    margin_pct: float
    viability: str
    nearby_upcoming: int
    uc_unsold_nearby: int
    verdict: str  # BUY / HOLD / PASS
    headline: str
    actions: list[str]


def evaluate_land_decision(
    *,
    micro_market: str | None = None,
    assumed_sale_psf: float = 9000.0,
    construction_cost_psf: float | None = None,
) -> LandDecision:
    """
    Land Intelligence decision sheet — extends margin + competition signals.
    Reuses adapter land/upcoming/UC; does not duplicate margin math.
    """
    adapter = get_adapter()
    land = adapter.land_prices()
    upcoming = adapter.upcoming()
    uc = adapter.under_construction()
    mm = micro_market or settings.MICRO_MARKET_DEFAULT
    land_psf = _nearest_land(mm, land)
    if land_psf != land_psf:  # NaN
        land_psf = float(land["land_price_psf"].median()) if not land.empty else 4500.0
    build_cost = construction_cost_psf if construction_cost_psf is not None else settings.CONSTRUCTION_COST_PSF
    loaded = land_psf * settings.LAND_FSI_LOAD_FACTOR
    sale = float(assumed_sale_psf)
    margin_psf = sale - loaded - build_cost
    margin_pct = (margin_psf / sale * 100) if sale else 0.0
    viability = _viability_label(margin_pct)

    # Lightweight rivalry pressure (seed-aware)
    up_n = len(upcoming) if not upcoming.empty else 0
    uc_unsold = int(uc["unsold_units"].sum()) if not uc.empty else 0

    if viability == "Unviable" or margin_pct < settings.MARGIN_STRESSED_PCT:
        verdict = "PASS"
        headline = "Do not acquire at this land basis — exit price cannot clear target margin."
        actions = [
            f"Re-trade land toward ≤ ₹{int(sale * 0.35 / settings.LAND_FSI_LOAD_FACTOR):,}/sqft loaded basis, or raise exit price.",
            "Require seller price cut before LOI; model again on Competition → Margin tab.",
            "If strategic, phase smaller plot / JV to de-risk cash.",
        ]
    elif viability == "Stressed" or up_n >= 3 or uc_unsold > 500:
        verdict = "HOLD"
        headline = "Margin is thin or supply pressure is elevated — diligence only, no hard bid yet."
        actions = [
            "Complete Competition density check (upcoming + UC unsold) before earnest money.",
            f"Stress-test exit at ₹{int(sale * 0.95):,}/sqft on Digital Twin / Co-pilot.",
            "Cap marketing pre-launch until absorption proof on comparable inventory.",
        ]
    else:
        verdict = "BUY"
        headline = "Land basis supports target margin under current seed competition set."
        actions = [
            "Proceed to title / layout diligence with margin floor locked in IC note.",
            "Pre-clear launch price band on Executive Hub before brochure.",
            "Monitor upcoming ads weekly — HOLD if High-threat rivals appear.",
        ]

    return LandDecision(
        micro_market=mm,
        land_price_psf=round(float(land_psf), 0),
        assumed_sale_psf=round(sale, 0),
        construction_cost_psf=round(float(build_cost), 0),
        loaded_land_psf=round(float(loaded), 0),
        margin_pct=round(float(margin_pct), 1),
        viability=viability,
        nearby_upcoming=up_n,
        uc_unsold_nearby=uc_unsold,
        verdict=verdict,
        headline=headline,
        actions=actions,
    )
