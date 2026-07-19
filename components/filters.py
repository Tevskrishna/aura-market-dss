"""Global filter bar — Project, Builder, Date range, Quarter."""
from __future__ import annotations

from datetime import date

import streamlit as st

from config import settings
from models.market import FilterState
from services.market_service import get_filter_options


def render_global_filters(key_prefix: str = "market") -> FilterState:
    opts = get_filter_options()
    st.sidebar.markdown(
        '<div style="font-size:0.72rem;font-weight:700;letter-spacing:0.08em;'
        'text-transform:uppercase;color:#9db4c7;margin:0.35rem 0 0.55rem;">Global filters</div>',
        unsafe_allow_html=True,
    )

    builder = st.sidebar.selectbox(
        "Builder",
        opts["builders"],
        key=f"{key_prefix}_builder",
    )
    project = st.sidebar.selectbox(
        "Project",
        opts["projects"],
        key=f"{key_prefix}_project",
    )

    c1, c2 = st.sidebar.columns(2)
    date_start = c1.date_input(
        "From",
        value=opts["min_date"],
        min_value=opts["min_date"],
        max_value=opts["max_date"],
        key=f"{key_prefix}_from",
    )
    date_end = c2.date_input(
        "To",
        value=opts["max_date"],
        min_value=opts["min_date"],
        max_value=opts["max_date"],
        key=f"{key_prefix}_to",
    )
    if isinstance(date_start, date) and isinstance(date_end, date) and date_start > date_end:
        st.sidebar.error("Start date must be on or before end date.")
        date_start, date_end = opts["min_date"], opts["max_date"]

    quarter = st.sidebar.selectbox(
        "Quarter",
        opts["quarters"],
        key=f"{key_prefix}_quarter",
    )

    return FilterState(
        builder=builder,
        project=project,
        date_start=date_start if isinstance(date_start, date) else None,
        date_end=date_end if isinstance(date_end, date) else None,
        quarter=quarter,
    )
