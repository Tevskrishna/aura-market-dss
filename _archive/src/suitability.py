from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor


FLOOD_MAP = {"Low": 1.0, "Medium": 0.55, "High": 0.2}


def _features(df: pd.DataFrame) -> pd.DataFrame:
    out = pd.DataFrame(
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
    return out


def suitability_scores(zones: pd.DataFrame) -> pd.DataFrame:
    """Train a small RF on engineered labels, score 0–100."""
    X = _features(zones)
    # Pseudo-label for training: amenity + growth - flood - distance penalties
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
    model = RandomForestRegressor(n_estimators=120, random_state=42)
    model.fit(X, y)
    pred = np.clip(model.predict(X), 0, 100)
    out = zones.copy()
    out["suitability_score"] = pred.round(0).astype(int)
    out["suitability_label"] = out["suitability_score"].apply(_label)
    return out


def _label(score: int) -> str:
    if score >= 85:
        return "Highly Suitable"
    if score >= 70:
        return "Suitable"
    if score >= 55:
        return "Moderate"
    return "Challenging"


def explain_zone(row: pd.Series) -> list[tuple[str, str]]:
    checks = [
        ("Flood Risk", f"{row['flood_risk']}", "✅" if row["flood_risk"] == "Low" else "⚠️"),
        ("Road / Highway", f"{row['highway_km']} km", "✅" if row["highway_km"] <= 3 else "⚠️"),
        ("Metro Access", f"{row['metro_km']} km", "✅" if row["metro_km"] <= 2 else "⚠️"),
        ("Population Growth", f"{row['population_growth_index']}/100", "⭐" if row["population_growth_index"] >= 75 else "·"),
        ("Price Trend YoY", f"{row['price_trend_yoy_pct']}%", "⭐" if row["price_trend_yoy_pct"] >= 8 else "·"),
        ("Hospitals nearby", str(int(row["hospitals"])), "✅" if row["hospitals"] >= 4 else "·"),
        ("Schools nearby", str(int(row["schools"])), "✅" if row["schools"] >= 6 else "·"),
    ]
    return checks
