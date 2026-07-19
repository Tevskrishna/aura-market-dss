"""
Market Overview business logic (MEASURE).

Why: Computes CTQ KPIs and chart-ready series without Streamlit imports.
Solves: Developers need a single trusted scorecard of micro-market health.
DMAIC: DEFINE KPIs + MEASURE absorption, bookings, marketing efficiency.
Reuse: Same MarketBundle feeds DMAIC, Forecasting baselines, Twin priors.
"""
from __future__ import annotations

import pandas as pd

from models.market import FilterState, MarketBundle, MarketKPIs
from services.data_loader import DataCatalog, load_catalog
from services.filter_service import apply_filters, build_filter_options


def get_validation_report():
    return load_catalog().report


def get_filter_options(catalog: DataCatalog | None = None) -> dict:
    catalog = catalog or load_catalog()
    return build_filter_options(catalog)


def compute_kpis(
    projects: pd.DataFrame,
    bookings: pd.DataFrame,
    marketing: pd.DataFrame,
    monthly: pd.DataFrame | None = None,
) -> MarketKPIs:
    total_projects = int(projects["project"].nunique()) if not projects.empty else 0
    total_units = int(projects["total_units"].sum()) if not projects.empty else 0
    units_sold = int(projects["units_sold"].sum()) if not projects.empty else 0
    absorption = round(units_sold / total_units * 100, 1) if total_units else 0.0
    active_builders = int(projects["developer"].nunique()) if not projects.empty else 0

    bookings_count = int(len(bookings)) if not bookings.empty else 0
    if not bookings.empty and "Apartment Sub Type" in bookings.columns:
        dist = bookings["Apartment Sub Type"].value_counts().to_dict()
        buyer_distribution = {str(k): int(v) for k, v in dist.items()}
    else:
        buyer_distribution = {}

    marketing_spend = float(marketing["spend_cr"].sum()) if not marketing.empty else 0.0

    # Period sales value: join filtered monthly units to project pricing when available
    sales_value = 0.0
    if monthly is not None and not monthly.empty and not projects.empty:
        price = projects[["project", "price_psf", "avg_unit_size_sqft"]].drop_duplicates("project")
        m = monthly.merge(price, on="project", how="left")
        m["sales_value_cr"] = m["units_sold_month"] * m["avg_unit_size_sqft"] * m["price_psf"] / 1e7
        sales_value = float(m["sales_value_cr"].fillna(0).sum())
    elif not projects.empty and "sales_value_cr" in projects.columns:
        sales_value = float(projects["sales_value_cr"].sum())

    return MarketKPIs(
        total_projects=total_projects,
        total_units=total_units,
        bookings=bookings_count,
        marketing_spend_cr=round(marketing_spend, 2),
        sales_value_cr=round(sales_value, 2),
        absorption_rate_pct=absorption,
        active_builders=active_builders,
        buyer_distribution=buyer_distribution,
    )


def build_market_bundle(filters: FilterState, catalog: DataCatalog | None = None) -> MarketBundle:
    catalog = catalog or load_catalog()
    if not catalog.report or not catalog.report.ready_for_market_overview:
        raise RuntimeError("Core datasets failed validation — Market Overview cannot run.")

    filtered = apply_filters(catalog, filters)
    kpis = compute_kpis(
        filtered["projects"],
        filtered["bookings"],
        filtered["marketing"],
        monthly=filtered["monthly"],
    )
    return MarketBundle(
        projects=filtered["projects"],
        monthly=filtered["monthly"],
        bookings=filtered["bookings"],
        marketing=filtered["marketing"],
        kpis=kpis,
    )


def booking_trend_frame(bookings: pd.DataFrame) -> pd.DataFrame:
    if bookings.empty:
        return pd.DataFrame(columns=["month", "bookings"])
    s = (
        bookings.assign(month=bookings["Created Date"].dt.to_period("M").dt.to_timestamp())
        .groupby("month", as_index=False)
        .size()
        .rename(columns={"size": "bookings"})
    )
    return s


def project_comparison_frame(projects: pd.DataFrame) -> pd.DataFrame:
    if projects.empty:
        return pd.DataFrame(columns=["project", "absorption_pct", "units_sold", "units_unsold"])
    cols = ["project", "developer", "absorption_pct", "units_sold", "units_unsold", "total_units"]
    return projects[cols].sort_values("absorption_pct", ascending=True)


def quarterly_performance_frame(monthly: pd.DataFrame, bookings: pd.DataFrame) -> pd.DataFrame:
    rows = []
    if not monthly.empty:
        m = monthly.groupby("fy_quarter", as_index=False)["units_sold_month"].sum()
        m = m.rename(columns={"units_sold_month": "units_sold"})
        rows.append(m)
    if not bookings.empty and "fy_quarter" in bookings.columns:
        b = bookings.groupby("fy_quarter", as_index=False).size().rename(columns={"size": "bookings"})
        if rows:
            out = rows[0].merge(b, on="fy_quarter", how="outer").fillna(0)
        else:
            out = b.assign(units_sold=0)
        return out.sort_values("fy_quarter")
    if rows:
        return rows[0].assign(bookings=0).sort_values("fy_quarter")
    return pd.DataFrame(columns=["fy_quarter", "units_sold", "bookings"])


def marketing_efficiency_frame(
    marketing: pd.DataFrame, bookings: pd.DataFrame, projects: pd.DataFrame
) -> pd.DataFrame:
    """Spend (₹ Cr) vs outcomes — efficiency / ROI base for MEASURE."""
    if marketing.empty:
        return pd.DataFrame(
            columns=["project", "spend_cr", "bookings", "sales_value_cr", "efficiency", "roi_sales", "roi_bookings"]
        )

    spend = marketing.groupby("project", as_index=False)["spend_cr"].sum()

    if not bookings.empty:
        bcounts = bookings.groupby("project").size().to_dict()
    else:
        bcounts = {}

    sales_map = {}
    if not projects.empty and "sales_value_cr" in projects.columns:
        sales_map = projects.groupby("project")["sales_value_cr"].sum().to_dict()

    records = []
    for _, row in spend.iterrows():
        name = str(row["project"])
        bk = 0
        for bp, cnt in bcounts.items():
            if bp.lower() in name.lower() or name.lower() in bp.lower():
                bk += cnt
        sv = 0.0
        for sp, val in sales_map.items():
            if sp.lower() in name.lower() or name.lower().split()[0] in sp.lower():
                sv += float(val)
        spend_cr = float(row["spend_cr"])
        roi_sales = (sv / spend_cr) if spend_cr > 0 else 0.0
        roi_bookings = (bk / spend_cr) if spend_cr > 0 else 0.0
        efficiency = roi_sales if sv > 0 else roi_bookings
        records.append(
            {
                "project": name,
                "spend_cr": round(spend_cr, 2),
                "bookings": bk,
                "sales_value_cr": round(sv, 2),
                "efficiency": round(efficiency, 2),
                "roi_sales": round(roi_sales, 2),
                "roi_bookings": round(roi_bookings, 2),
            }
        )
    return pd.DataFrame(records).sort_values("spend_cr", ascending=False)
