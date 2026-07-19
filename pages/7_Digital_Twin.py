"""Digital Twin — AURA-Market cannibalization + intervention simulator."""
from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from components.kpi_cards import render_kpi_cards
from components.layout import page_hero, require_login, section_label
from services.adapters import get_adapter
from services.twin_service import run_twin_with_cannibalization
from utils.dmaic_charts import twin_curves

st.set_page_config(page_title="Digital Twin", page_icon="🕹️", layout="wide")
require_login()

page_hero(
    kicker="AURA-Market · PRESCRIBE",
    title="Digital Twin + Competitive Cannibalization",
    subtitle="Inject a rival launch into the simulation — quantify pipeline loss, then test price cut / subvention recovery.",
    chips=[("SimPy-style engine", "ok"), ("Budget buyer diversion", "ok"), ("Rival trigger", "")],
)

df = get_adapter().projects()
upcoming = get_adapter().upcoming()
project = st.selectbox("My project", df["project"].tolist())
row = df[df["project"] == project].iloc[0]

base = st.slider("Base monthly sales rate", 5, 80, max(int(row["units_sold"] / 24), 8))
months = st.slider("Simulation duration (months)", 6, 24, 12)
intervene = st.slider("My intervention month (0 = none)", 0, months, 4)
cut = st.slider("My price cut %", 0, 20, 8)
subvention = st.checkbox("Inject subvention at intervention", True)

st.sidebar.markdown("##### Rival launch (blind spot)")
enable_rival = st.sidebar.checkbox("Enable competitor launch trigger", True)
default_rival_price = int(min(float(row["price_psf"]) * 0.92, float(upcoming["indicative_price_psf"].min()) if not upcoming.empty else row["price_psf"] * 0.9))
rival_month = st.sidebar.slider("Competitor launch month", 1, months, 3)
rival_price = st.sidebar.number_input("Competitor price ₹/sqft", 4000, 20000, default_rival_price, 100)

ticket = row["avg_unit_size_sqft"] * row["price_psf"] / 100_000
result = run_twin_with_cannibalization(
    base_monthly_rate=base,
    months=months,
    price_psf=float(row["price_psf"]),
    construction_progress=float(row["construction_progress_pct"]),
    avg_ticket_lakhs=float(ticket),
    intervene_month=intervene or None,
    price_cut_pct=float(cut),
    subvention=subvention,
    competitor_launch_month=rival_month if enable_rival else None,
    competitor_price_psf=float(rival_price) if enable_rival else None,
)

section_label("Cumulative units — baseline vs cannibalization vs intervention")
st.plotly_chart(
    twin_curves(result.months, result.baseline, result.intervention, result.cannibalized),
    width="stretch",
)

render_kpi_cards(
    [
        {"label": "Baseline revenue", "value": result.revenue_baseline_cr, "format": "cr"},
        {"label": "Under rival attack", "value": result.revenue_cannibal_cr, "format": "cr"},
        {"label": "Blind-spot loss", "value": result.cannibal_loss_cr, "format": "cr"},
        {"label": "Recovery vs rival", "value": result.recovery_cr, "format": "cr"},
    ]
)
st.info(
    "When a cheaper rival launches, **budget buyers divert first**, then a share of normal demand. "
    "Prescriptive interventions (cut + subvention) push recovery while the rival is active."
)
