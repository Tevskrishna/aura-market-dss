"""Market Overview — Phase-1 Page 1 + foundation scorecard."""
from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from components.filters import render_global_filters
from components.kpi_cards import render_kpi_cards
from components.layout import page_hero, require_login, section_label
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
render_kpi_cards(
    [
        {"label": "Total Units Launched", "value": sk["total_units"], "format": "int"},
        {"label": "Units Sold", "value": sk["units_sold"], "format": "int"},
        {"label": "Units Unsold", "value": sk["units_unsold"], "format": "int"},
        {"label": "Sigma Level (σ)", "value": sk["sigma_level"], "format": "float"},
        {"label": "At-Risk Projects", "value": sk["at_risk_projects"], "format": "int", "help": "Absorption < 70%"},
    ],
    columns=5,
)
st.caption(f"DPMO = (unsold ÷ launched) × 1,000,000 → **{sk['dpmo']:,.0f}**")

section_label("Absorption & mix")
c1, c2 = st.columns([1.3, 1])
with c1:
    st.plotly_chart(absorption_band_chart(bundle.projects), width="stretch")
with c2:
    st.plotly_chart(sold_unsold_donut(sk["units_sold"], sk["units_unsold"]), width="stretch")

st.plotly_chart(price_absorption_bubble(bundle.projects), width="stretch")

section_label("Bookings pulse")
a, b = st.columns([1.25, 1])
with a:
    st.plotly_chart(booking_trend_chart(booking_trend_frame(bundle.bookings)), width="stretch")
with b:
    st.plotly_chart(buyer_mix_chart(bundle.kpis.buyer_distribution), width="stretch")

section_label("Inventory detail")
cols = [c for c in ["developer", "project", "total_units", "units_sold", "units_unsold", "absorption_pct", "price_psf", "status"] if c in bundle.projects.columns]
st.dataframe(bundle.projects[cols], width="stretch", hide_index=True)
