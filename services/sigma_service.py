from __future__ import annotations

import math

import numpy as np
import pandas as pd


DPMO_TABLE = [
    (308537, 0.5),
    (226627, 1.0),
    (158655, 1.5),
    (66807, 2.0),
    (22750, 2.5),
    (6210, 3.0),
    (1350, 3.5),
    (233, 4.0),
    (32, 4.5),
    (3.4, 5.0),
    (0.57, 5.5),
    (0.002, 6.0),
]


def dpmo(unsold: float, total: float) -> float:
    if total <= 0:
        return 0.0
    return float(unsold) / float(total) * 1_000_000


def sigma_from_dpmo(dpmo_value: float) -> float:
    if dpmo_value >= DPMO_TABLE[0][0]:
        return DPMO_TABLE[0][1]
    for i in range(len(DPMO_TABLE) - 1):
        d1, s1 = DPMO_TABLE[i]
        d2, s2 = DPMO_TABLE[i + 1]
        if d2 <= dpmo_value <= d1:
            t = (math.log(d1) - math.log(max(dpmo_value, 1e-9))) / (math.log(d1) - math.log(d2))
            return round(s1 + t * (s2 - s1), 2)
    return 6.0


def market_kpis(df: pd.DataFrame) -> dict:
    total = int(df["total_units"].sum())
    sold = int(df["units_sold"].sum())
    unsold = int(df["units_unsold"].sum())
    d = dpmo(unsold, total)
    at_risk = int((df["absorption_pct"] < 70).sum())
    return {
        "total_units": total,
        "units_sold": sold,
        "units_unsold": unsold,
        "absorption_pct": round(sold / total * 100, 1) if total else 0,
        "dpmo": round(d, 0),
        "sigma_level": sigma_from_dpmo(d),
        "at_risk_projects": at_risk,
    }


def augment_for_ml(df: pd.DataFrame, copies: int = 10, sigma_frac: float = 0.05) -> pd.DataFrame:
    """Gaussian noise augmentation to reduce overfitting on small n."""
    numeric = [
        "price_psf",
        "avg_unit_size_sqft",
        "construction_delay_months",
        "construction_progress_pct",
        "brand_score",
        "total_units",
    ]
    frames = [df]
    rng = np.random.default_rng(7)
    for _ in range(copies - 1):
        noise = df.copy()
        for col in numeric:
            std = float(df[col].std() or 1)
            noise[col] = noise[col] + rng.normal(0, sigma_frac * std, len(df))
        noise["absorption_pct"] = np.clip(
            noise["absorption_pct"] + rng.normal(0, 2, len(df)), 5, 100
        )
        frames.append(noise)
    return pd.concat(frames, ignore_index=True)
