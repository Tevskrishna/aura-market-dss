"""Market Overview — interactive MEASURE scorecard (click KPIs / lenses / actions)."""
from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from components.filters import render_global_filters
from components.executive_sheet import render_executive_sheet
from components.layout import page_hero, require_login, section_label
from components.states import empty_state, error_state
from components.viz_studio import generate_button, graphic_html, live_kpi_strip, render_dynamic_figure, scenario_bar
from services.decision_brief_service import brief_from_market
from services.data_loader import load_catalog
from services.market_service import booking_trend_frame, build_market_bundle, get_validation_report
from services.sigma_service import market_kpis as sigma_kpis
from utils.charts import booking_trend_chart, buyer_mix_chart
from utils.dmaic_charts import absorption_band_chart, price_absorption_bubble

st.set_page_config(page_title="Market Overview", page_icon="📊", layout="wide")
require_login("Market Intelligence")

report = get_validation_report()
page_hero(
    kicker="MEASURE · Market",
    title="Market Intelligence",
    subtitle="Confirm demand health before the launch call — KPI lenses update the graphic live.",
    compact=True,
)

if not report or not report.ready_for_market_overview:
    error_state(
        "Core datasets failed validation",
        "Market overview cannot load until catalog validation passes.",
    )
    st.stop()

filters = render_global_filters("market")
bundle = build_market_bundle(filters, load_catalog())
sk = sigma_kpis(bundle.projects)
projects = bundle.projects

if projects.empty:
    empty_state(
        "No projects in filtered market view",
        "Widen filters or reset to all builders / projects.",
        "Clear filters in the control strip above.",
    )
    st.stop()

render_executive_sheet(
    brief_from_market(
        absorption_pct=float(sk["absorption_pct"]),
        at_risk=int(sk["at_risk_projects"]),
        dpmo=float(sk["dpmo"]),
        unsold=int(sk["units_unsold"]),
    ),
    key="mkt_eds",
)

section_label("Six Sigma scorecard — tap to focus")
live_kpi_strip(
    [
        {"label": "Launched", "display": f"{sk['total_units']:,}", "hint": "units"},
        {"label": "Sold", "display": f"{sk['units_sold']:,}", "hint": "units"},
        {"label": "Unsold", "display": f"{sk['units_unsold']:,}", "hint": "defect pool"},
        {"label": "Sigma", "display": str(sk["sigma_level"]), "hint": "DPMO-based"},
        {"label": "At-risk", "display": str(sk["at_risk_projects"]), "hint": "<70% abs."},
    ]
)
st.caption(f"DPMO = (unsold ÷ launched) × 1,000,000 → **{sk['dpmo']:,.0f}**")

k1, k2, k3, k4 = st.columns(4)
with k1:
    if st.button("Focus at-risk", type="primary", width="stretch", key="mkt_focus_risk"):
        st.session_state["mkt_focus"] = "at_risk"
        st.session_state["mkt_lens"] = "Absorption bands"
with k2:
    if st.button("Show sold-out", width="stretch", key="mkt_focus_sold"):
        st.session_state["mkt_focus"] = "sold_out"
        st.session_state["mkt_lens"] = "Price bubble"
with k3:
    if st.button("Bookings pulse", width="stretch", key="mkt_focus_book"):
        st.session_state["mkt_focus"] = "all"
        st.session_state["mkt_lens"] = "Bookings pulse"
with k4:
    if st.button("Reset view", width="stretch", key="mkt_focus_reset"):
        st.session_state["mkt_focus"] = "all"
        st.session_state["mkt_lens"] = "Absorption bands"

focus = st.session_state.get("mkt_focus", "all")
if focus == "at_risk":
    view = projects[projects["absorption_pct"] < 70].sort_values("absorption_pct")
    st.info(f"Focused on **{len(view)}** at-risk projects (<70% absorption).")
elif focus == "sold_out":
    view = projects[projects["absorption_pct"] >= 95].sort_values("absorption_pct", ascending=False)
    st.success(f"Showing **{len(view)}** sold-out / near sold-out benchmarks.")
else:
    view = projects

a1, a2, a3 = st.columns(3)
with a1:
    if st.button("→ Open AI Recommendations", width="stretch", key="mkt_go_recs"):
        from components.touch_nav import navigate_to

        navigate_to("AI Recommendations", "pages/8_AI_Recommendations.py")
with a2:
    if st.button("→ Open Builder Deep Dive", width="stretch", key="mkt_go_builder"):
        from components.touch_nav import navigate_to

        navigate_to("Project Deep Dive", "pages/6_Builder_Deep_Dive.py")
with a3:
    if st.button("→ Open Digital Twin", width="stretch", key="mkt_go_twin"):
        from components.touch_nav import navigate_to

        navigate_to("Digital Twin", "pages/7_Digital_Twin.py")

section_label("Interactive market graphics — change lens to redraw")
graphic_html("trend-pulse.svg", "dss-graphic")
lens = scenario_bar(
    "mkt_lens",
    "Chart lens (tap to switch figure)",
    ["Absorption bands", "Price bubble", "Bookings pulse", "Buyer mix"],
)
generate_button("mkt_studio", "Regenerate market graphics")


def _mkt_fig():
    frame = view if not view.empty else projects
    if lens == "Absorption bands":
        return absorption_band_chart(frame)
    if lens == "Price bubble":
        return price_absorption_bubble(frame)
    if lens == "Bookings pulse":
        return booking_trend_chart(booking_trend_frame(bundle.bookings))
    return buyer_mix_chart(bundle.kpis.buyer_distribution)


render_dynamic_figure("mkt_studio", _mkt_fig, height=420, scene=f"{lens}|{focus}|{len(view)}")
st.caption("Plotly chart is zoomable · pan · hover · box-select. Use the mode bar at the top-right of the figure.")

section_label("Inventory detail — click column headers to sort")
cols = [
    c
    for c in [
        "developer",
        "project",
        "total_units",
        "units_sold",
        "units_unsold",
        "absorption_pct",
        "price_psf",
        "status",
    ]
    if c in view.columns
]
st.dataframe(view[cols], width="stretch", hide_index=True, height=360)
