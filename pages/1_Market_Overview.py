"""Market Overview — Phase-1 Page 1 + foundation scorecard."""
from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from components.filters import render_global_filters
from components.kpi_cards import render_kpi_cards
from components.layout import decision_action, page_hero, require_login, section_label
from components.viz_studio import generate_button, graphic_html, live_kpi_strip, render_dynamic_figure, scenario_bar
from services.data_loader import load_catalog
from services.market_service import build_market_bundle, get_validation_report
from services.sigma_service import market_kpis as sigma_kpis
from utils.charts import booking_trend_chart, buyer_mix_chart
from utils.dmaic_charts import absorption_band_chart, price_absorption_bubble, sold_unsold_donut
from services.market_service import booking_trend_frame

st.set_page_config(page_title="Market Overview", page_icon="📊", layout="wide")
require_login()

report = get_validation_report()
page_hero(
    kicker="Phase 1 · MEASURE",
    title="Market Overview",
    subtitle="Bagaluru micro-market scorecard — units, absorption bands, Six Sigma DPMO, and price dynamics.",
    chips=[("DMAIC Page 1", "ok"), ("Sigma / DPMO", "ok"), ("Builder filter", "")],
)

if not report or not report.ready_for_market_overview:
    st.error("Core datasets failed validation.")
    st.stop()

filters = render_global_filters("market")
bundle = build_market_bundle(filters, load_catalog())
sk = sigma_kpis(bundle.projects)

section_label("Six Sigma scorecard")
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

decision_action(
    "This week's market moves",
    [
        f"Escalate {sk['at_risk_projects']} at-risk project(s) (absorption <70%) to AI Recommendations.",
        "Compare red-band projects vs sold-out benchmarks on Builder Deep Dive.",
        "If DPMO stays high, prioritize IMPROVE actions before the next launch quarter.",
    ],
    tone="warn" if sk["at_risk_projects"] else "ok",
)

section_label("Interactive market graphics")
graphic_html("trend-pulse.svg", "dss-graphic")
lens = scenario_bar("mkt_lens", "Chart lens", ["Absorption bands", "Price bubble", "Bookings pulse", "Buyer mix"])
generate_button("mkt_studio", "Regenerate market graphics")


def _mkt_fig():
    if lens == "Absorption bands":
        return absorption_band_chart(bundle.projects)
    if lens == "Price bubble":
        return price_absorption_bubble(bundle.projects)
    if lens == "Bookings pulse":
        return booking_trend_chart(booking_trend_frame(bundle.bookings))
    return buyer_mix_chart(bundle.kpis.buyer_distribution)


render_dynamic_figure("mkt_studio", _mkt_fig, height=420, scene=str(lens))

c1, c2 = st.columns(2)
with c1:
    st.plotly_chart(sold_unsold_donut(sk["units_sold"], sk["units_unsold"]), width="stretch")
with c2:
    st.plotly_chart(absorption_band_chart(bundle.projects), width="stretch")

section_label("Inventory detail")
cols = [c for c in ["developer", "project", "total_units", "units_sold", "units_unsold", "absorption_pct", "price_psf", "status"] if c in bundle.projects.columns]
st.dataframe(bundle.projects[cols], width="stretch", hide_index=True)
