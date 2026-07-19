from __future__ import annotations

import numpy as np
import pandas as pd

D2 = 1.128
D4 = 3.267


def imr_chart(series: pd.Series) -> dict:
    x = series.astype(float).dropna().reset_index(drop=True)
    if len(x) < 3:
        return {"ok": False, "reason": "Need at least 3 points"}
    mr = x.diff().abs().dropna()
    xbar = float(x.mean())
    mrbar = float(mr.mean())
    sigma = mrbar / D2 if D2 else 0
    ucl = xbar + 3 * sigma
    lcl = max(xbar - 3 * sigma, 0)
    mr_ucl = D4 * mrbar

    ooc = []
    for i, val in enumerate(x):
        if val > ucl or val < lcl:
            ooc.append({"index": i, "value": float(val), "rule": ">3σ (I-chart)"})

    # Western Electric-ish runs
    side = np.sign(x - xbar)
    run = 1
    for i in range(1, len(side)):
        if side[i] == side[i - 1] and side[i] != 0:
            run += 1
            if run >= 8:
                ooc.append({"index": i, "value": float(x[i]), "rule": "8 consecutive same side of CL"})
                break
        else:
            run = 1

    diffs = np.diff(x)
    up = 0
    down = 0
    for i, d in enumerate(diffs, start=1):
        if d > 0:
            up += 1
            down = 0
        elif d < 0:
            down += 1
            up = 0
        else:
            up = down = 0
        if up >= 6:
            ooc.append({"index": i, "value": float(x[i]), "rule": "6-point upward trend"})
            break
        if down >= 6:
            ooc.append({"index": i, "value": float(x[i]), "rule": "6-point downward trend"})
            break

    return {
        "ok": True,
        "x": x,
        "mr": mr.reset_index(drop=True),
        "xbar": xbar,
        "mrbar": mrbar,
        "sigma": sigma,
        "ucl": ucl,
        "lcl": lcl,
        "mr_ucl": mr_ucl,
        "ooc": ooc,
    }


def forecast_linear_seasonal(series: pd.Series, months: int = 6) -> pd.DataFrame:
    y = series.astype(float).values
    n = len(y)
    x = np.arange(n)
    coef = np.polyfit(x, y, 1)
    trend = np.poly1d(coef)
    resid = y - trend(x)
    season = float(np.mean(resid[-12:])) if n >= 12 else float(np.mean(resid))
    sigma = float(np.std(resid)) if n > 2 else 1.0
    rows = []
    for i in range(months):
        idx = n + i
        pred = float(trend(idx) + 0.25 * season * np.sin(2 * np.pi * (idx % 12) / 12))
        rows.append(
            {
                "step": i + 1,
                "forecast": round(pred, 2),
                "lower": round(pred - 1.96 * sigma, 2),
                "upper": round(pred + 1.96 * sigma, 2),
            }
        )
    return pd.DataFrame(rows)
