"""Marketing Intelligence — MEASURE SMC spend → bookings → ROI → recommendations."""
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
    roi: pd.DataFrame
    share_long: pd.DataFrame
    reallocation: list[dict]
    top_channel_hint: str


def melt_smc_share(df: pd.DataFrame) -> pd.DataFrame:
    """Wide FY-Qn share matrix → long project / fy_quarter / spend_share."""
    if df is None or df.empty or "project" not in df.columns:
        return pd.DataFrame(columns=["project", "fy_quarter", "spend_share"])
    id_col = "project"
    value_cols = [c for c in df.columns if c != id_col]
    long = df.melt(id_vars=[id_col], value_vars=value_cols, var_name="fy_quarter", value_name="spend_share")
    long["project"] = long["project"].astype(str).str.strip()
    long["spend_share"] = pd.to_numeric(long["spend_share"], errors="coerce").fillna(0.0)
    long = long[long["spend_share"] > 0].copy()
    return long.reset_index(drop=True)


def project_roi_frame(efficiency: pd.DataFrame) -> pd.DataFrame:
    """Attach ROI labels and quartiles to efficiency frame."""
    if efficiency is None or efficiency.empty:
        return pd.DataFrame(
            columns=[
                "project",
                "spend_cr",
                "bookings",
                "sales_value_cr",
                "roi_sales",
                "roi_bookings",
                "roi_score",
                "quartile",
                "verdict",
            ]
        )
    out = efficiency.copy()
    spend = out["spend_cr"].replace(0, pd.NA)
    out["roi_sales"] = (out["sales_value_cr"] / spend).fillna(0).round(2)
    out["roi_bookings"] = (out["bookings"] / spend).fillna(0).round(2)
    # Prefer sales ROI when available; else bookings per ₹ Cr
    out["roi_score"] = out.apply(
        lambda r: float(r["roi_sales"]) if r["roi_sales"] > 0 else float(r["roi_bookings"]),
        axis=1,
    ).round(2)
    try:
        out["quartile"] = pd.qcut(out["roi_score"].rank(method="first"), 4, labels=["Q4-Low", "Q3", "Q2", "Q1-High"])
    except ValueError:
        out["quartile"] = "Mid"
    out["verdict"] = out["quartile"].map(
        {
            "Q1-High": "Boost / scale",
            "Q2": "Hold",
            "Q3": "Review mix",
            "Q4-Low": "Cut / reallocate",
            "Mid": "Monitor",
        }
    ).fillna("Monitor")
    return out.sort_values("roi_score", ascending=False).reset_index(drop=True)


def marketing_reallocation_recs(roi: pd.DataFrame, top_n: int = 3) -> list[dict]:
    """Prescriptive cut / hold / boost actions from ROI quartiles."""
    if roi is None or roi.empty:
        return [
            {
                "project": "—",
                "issue": "No SMC spend linked",
                "action": "Load marketing_spends.csv and refresh filters",
                "detail": "Cannot optimize blind spend without ₹ Cr rows.",
            }
        ]
    recs: list[dict] = []
    lows = roi[roi["quartile"].astype(str).str.contains("Q4|Low", case=False, na=False)].head(top_n)
    highs = roi[roi["quartile"].astype(str).str.contains("Q1|High", case=False, na=False)].head(top_n)
    for _, r in lows.iterrows():
        recs.append(
            {
                "project": str(r["project"]),
                "issue": f"Bottom-quartile ROI ({r['roi_score']})",
                "action": "Freeze incremental SMC spend; reallocate budget",
                "detail": f"Spend ₹{r['spend_cr']} Cr → {int(r['bookings'])} bookings · sales ₹{r['sales_value_cr']} Cr",
            }
        )
    for _, r in highs.iterrows():
        recs.append(
            {
                "project": str(r["project"]),
                "issue": f"Top-quartile ROI ({r['roi_score']})",
                "action": "Shift share of cut budget into this project / channel",
                "detail": f"Bookings/₹Cr = {r['roi_bookings']} · Sales/₹Cr = {r['roi_sales']}",
            }
        )
    if not recs:
        best = roi.iloc[0]
        worst = roi.iloc[-1]
        recs = [
            {
                "project": str(worst["project"]),
                "issue": "Lowest relative ROI",
                "action": "Cut 10–20% SMC and redeploy",
                "detail": f"Move budget toward {best['project']}",
            }
        ]
    return recs


def build_marketing_insights(filters: FilterState) -> MarketingInsights:
    catalog = load_catalog()
    frames = apply_filters(catalog, filters)
    marketing = frames["marketing"]
    bookings = frames["bookings"]
    projects = frames["projects"]

    share_raw = catalog.get("marketing_spend_share") if catalog.has("marketing_spend_share") else pd.DataFrame()
    share_long = melt_smc_share(share_raw)

    if marketing.empty:
        empty = pd.DataFrame()
        return MarketingInsights(0.0, empty, empty, empty, empty, share_long, marketing_reallocation_recs(empty), "")

    by_q = marketing.groupby("fy_quarter", as_index=False)["spend_cr"].sum().sort_values("fy_quarter")
    by_p = marketing.groupby("project", as_index=False)["spend_cr"].sum().sort_values("spend_cr", ascending=False)
    eff = marketing_efficiency_frame(marketing, bookings, projects)
    roi = project_roi_frame(eff)
    recs = marketing_reallocation_recs(roi)

    hint = ""
    if not bookings.empty and "Primary Source" in bookings.columns:
        top = bookings["Primary Source"].astype(str).value_counts().head(1)
        if not top.empty:
            hint = f"Top booking channel: {top.index[0]} ({int(top.iloc[0]):,} bookings) — protect that mix when reallocating."

    return MarketingInsights(
        total_spend_cr=round(float(marketing["spend_cr"].sum()), 2),
        by_quarter=by_q,
        by_project=by_p,
        efficiency=eff,
        roi=roi,
        share_long=share_long,
        reallocation=recs,
        top_channel_hint=hint,
    )
