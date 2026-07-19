"""
Global filter options + application.

Shared by Market Overview today; Competition / DMAIC / Buyer will call the same API.
"""
from __future__ import annotations

from datetime import date

import pandas as pd

from config import settings
from models.market import FilterState
from services.data_loader import DataCatalog


def build_filter_options(catalog: DataCatalog) -> dict:
    projects = catalog.get("projects")
    monthly = catalog.get("monthly_absorption")
    bookings = catalog.get("buyer_demographics") if catalog.has("buyer_demographics") else pd.DataFrame()

    builders = sorted(projects["developer"].dropna().unique().tolist())
    project_names = sorted(projects["project"].dropna().unique().tolist())

    # Include booking-only project labels (Atmosphere etc.) for Buyer-linked filters
    if not bookings.empty:
        for p in bookings["project"].dropna().unique().tolist():
            if p not in project_names:
                project_names.append(p)
        project_names = sorted(project_names)

    quarters = sorted(
        set(monthly["fy_quarter"].dropna().unique().tolist())
        | (
            set(bookings["fy_quarter"].dropna().unique().tolist())
            if not bookings.empty and "fy_quarter" in bookings.columns
            else set()
        )
    )

    min_d = monthly["month"].min().date() if not monthly.empty else date(2022, 12, 1)
    max_d = monthly["month"].max().date() if not monthly.empty else date.today()
    if not bookings.empty:
        bmin = bookings["Created Date"].min()
        bmax = bookings["Created Date"].max()
        if pd.notna(bmin):
            min_d = min(min_d, bmin.date())
        if pd.notna(bmax):
            max_d = max(max_d, bmax.date())

    return {
        "builders": [settings.ALL_BUILDERS_LABEL] + builders,
        "projects": [settings.ALL_PROJECTS_LABEL] + project_names,
        "quarters": [settings.ALL_QUARTERS_LABEL] + quarters,
        "min_date": min_d,
        "max_date": max_d,
    }


def apply_filters(catalog: DataCatalog, filters: FilterState) -> dict[str, pd.DataFrame]:
    """
    Dimension filters (builder/project) apply to inventory + time series.
    Time filters (date/quarter) apply only to monthly, bookings, marketing —
    project master remains a point-in-time snapshot for stock KPIs.
    """
    projects = catalog.get("projects")
    monthly = catalog.get("monthly_absorption")
    bookings = catalog.get("buyer_demographics") if catalog.has("buyer_demographics") else pd.DataFrame()
    marketing = catalog.get("marketing_spends") if catalog.has("marketing_spends") else pd.DataFrame()

    if filters.builder != settings.ALL_BUILDERS_LABEL:
        projects = projects[projects["developer"] == filters.builder]
        monthly = monthly[monthly["developer"] == filters.builder]
        if not bookings.empty:
            bookings = bookings[bookings["developer"] == filters.builder]

    if filters.project != settings.ALL_PROJECTS_LABEL:
        projects = projects[projects["project"] == filters.project]
        monthly = monthly[monthly["project"] == filters.project]
        if not bookings.empty:
            bookings = bookings[bookings["project"] == filters.project]
        if not marketing.empty:
            token = filters.project.split()[0]
            marketing = marketing[marketing["project"].str.contains(token, case=False, na=False)]

    if filters.date_start:
        start = pd.Timestamp(filters.date_start)
        monthly = monthly[monthly["month"] >= start]
        if not bookings.empty:
            bookings = bookings[bookings["Created Date"] >= start]
        if not marketing.empty:
            marketing = marketing[marketing["period_start"] >= start]

    if filters.date_end:
        end = pd.Timestamp(filters.date_end) + pd.offsets.MonthEnd(0)
        monthly = monthly[monthly["month"] <= end]
        if not bookings.empty:
            bookings = bookings[bookings["Created Date"] <= end]
        if not marketing.empty:
            marketing = marketing[marketing["period_start"] <= end]

    if filters.quarter != settings.ALL_QUARTERS_LABEL:
        monthly = monthly[monthly["fy_quarter"] == filters.quarter]
        if not bookings.empty and "fy_quarter" in bookings.columns:
            bookings = bookings[bookings["fy_quarter"] == filters.quarter]
        if not marketing.empty and "fy_quarter" in marketing.columns:
            marketing = marketing[marketing["fy_quarter"] == filters.quarter]

    return {
        "projects": projects.reset_index(drop=True),
        "monthly": monthly.reset_index(drop=True),
        "bookings": bookings.reset_index(drop=True),
        "marketing": marketing.reset_index(drop=True),
    }
