"""
Bengaluru Map DSS service — suitability scoring + zone analytics.

Phase-2 Decision Support: WHERE to build.
"""
from __future__ import annotations

from functools import lru_cache

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor

from services.adapters import get_adapter

FLOOD_MAP = {"Low": 1.0, "Medium": 0.55, "High": 0.2}

# Representative Bengaluru metro stations for map overlays
METRO_STATIONS = pd.DataFrame(
    [
        ("Baiyyappanahalli", 12.990, 77.660, "Purple"),
        ("Indiranagar", 12.978, 77.640, "Purple"),
        ("MG Road", 12.975, 77.606, "Purple"),
        ("Majestic", 12.976, 77.572, "Purple/Green"),
        ("Yelachenahalli", 12.897, 77.570, "Green"),
        ("Jayanagar", 12.930, 77.584, "Green"),
        ("Nagasandra", 13.048, 77.500, "Green"),
        ("Yelahanka", 13.105, 77.596, "Yellow planned"),
        ("Hebbal", 13.035, 77.591, "Yellow planned"),
        ("KR Puram", 13.007, 77.696, "Purple"),
        ("Whitefield", 12.969, 77.749, "Purple"),
        ("Electronic City", 12.845, 77.663, "Yellow planned"),
        ("Silk Board", 12.917, 77.622, "Yellow planned"),
    ],
    columns=["station", "lat", "lon", "line"],
)


def _features(df: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "price": df["avg_price_psf"],
            "trend": df["price_trend_yoy_pct"],
            "metro": 1 / (1 + df["metro_km"]),
            "highway": 1 / (1 + df["highway_km"]),
            "hospitals": df["hospitals"],
            "schools": df["schools"],
            "malls": df["malls"],
            "parks": df["parks"],
            "flood": df["flood_risk"].map(FLOOD_MAP).fillna(0.5),
            "aqi_inv": 1 / (df["air_quality_index"] / 50),
            "pop_growth": df["population_growth_index"] / 100,
        }
    )


def _label(score: int) -> str:
    if score >= 85:
        return "Highly Suitable"
    if score >= 75:
        return "Suitable"
    if score >= 50:
        return "Moderate"
    return "High Risk"


@lru_cache(maxsize=1)
def scored_zones() -> pd.DataFrame:
    zones = get_adapter().zones()
    X = _features(zones)
    y = (
        25 * X["metro"]
        + 15 * X["highway"]
        + 2.5 * X["hospitals"]
        + 2.0 * X["schools"]
        + 2.0 * X["malls"]
        + 2.0 * X["parks"]
        + 20 * X["flood"]
        + 15 * X["pop_growth"]
        + 8 * np.clip(X["trend"] / 15, 0, 1)
        - 5 * np.clip((zones["avg_price_psf"] - 9000) / 5000, -0.5, 1)
    )
    y = np.clip(y, 20, 98)
    model = RandomForestRegressor(n_estimators=160, random_state=42)
    model.fit(X, y)
    out = zones.copy()
    out["suitability_score"] = np.clip(model.predict(X), 0, 100).round(0).astype(int)
    out["suitability_label"] = out["suitability_score"].apply(_label)
    return out


def map_home_kpis(df: pd.DataFrame) -> dict:
    top = df.sort_values("suitability_score", ascending=False).iloc[0]
    growth = df.sort_values("price_trend_yoy_pct", ascending=False).iloc[0]
    return {
        "areas_covered": int(len(df)),
        "avg_price_psf": float(df["avg_price_psf"].mean()),
        "highest_growth_area": str(growth["zone"]),
        "ai_top_pick": str(top["zone"]),
        "high_risk_zones": int((df["suitability_score"] < 50).sum()),
    }


def feature_importance(df: pd.DataFrame | None = None) -> pd.DataFrame:
    df = df if df is not None else scored_zones()
    X = _features(df)
    y = df["suitability_score"]
    model = RandomForestRegressor(n_estimators=160, random_state=42)
    model.fit(X, y)
    return (
        pd.DataFrame({"feature": X.columns, "importance": model.feature_importances_})
        .sort_values("importance", ascending=False)
        .reset_index(drop=True)
    )


def explain_zone(row: pd.Series) -> list[tuple[str, str, str]]:
    return [
        ("Flood Risk", f"{row['flood_risk']}", "ok" if row["flood_risk"] == "Low" else "warn"),
        ("Road / Highway", f"{row['highway_km']} km", "ok" if row["highway_km"] <= 3 else "warn"),
        ("Metro Access", f"{row['metro_km']} km", "ok" if row["metro_km"] <= 2 else "warn"),
        ("Population Growth", f"{int(row['population_growth_index'])}/100", "ok" if row["population_growth_index"] >= 75 else ""),
        ("Price Trend YoY", f"{row['price_trend_yoy_pct']}%", "ok" if row["price_trend_yoy_pct"] >= 8 else ""),
        ("Hospitals", str(int(row["hospitals"])), "ok" if row["hospitals"] >= 4 else ""),
        ("Schools", str(int(row["schools"])), "ok" if row["schools"] >= 6 else ""),
        ("Malls", str(int(row["malls"])), "ok" if row["malls"] >= 3 else ""),
        ("Parks", str(int(row["parks"])), "ok" if row["parks"] >= 3 else ""),
    ]


def radar_values(row: pd.Series) -> dict[str, float]:
    return {
        "Metro": max(0, 100 - row["metro_km"] * 18),
        "Hospitals": min(100, row["hospitals"] * 8),
        "Schools": min(100, row["schools"] * 6),
        "Roads": max(0, 100 - row["highway_km"] * 12),
        "Infrastructure": min(100, (row["malls"] + row["parks"]) * 8),
        "Population Growth": float(row["population_growth_index"]),
    }


def what_if_score(
    metro_km: float,
    highway_km: float,
    hospitals: int,
    schools: int,
    malls: int,
    parks: int,
    flood: str,
    pop_growth: float,
    price_psf: float,
    trend: float,
) -> float:
    flood_v = FLOOD_MAP.get(flood, 0.5)
    score = (
        25 * (1 / (1 + metro_km))
        + 15 * (1 / (1 + highway_km))
        + 2.5 * hospitals
        + 2.0 * schools
        + 2.0 * malls
        + 2.0 * parks
        + 20 * flood_v
        + 15 * (pop_growth / 100)
        + 8 * min(max(trend / 15, 0), 1)
        - 5 * min(max((price_psf - 9000) / 5000, -0.5), 1)
    )
    return float(np.clip(score, 0, 100))
