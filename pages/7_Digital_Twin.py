"""Digital Twin — AURA-Market cannibalization + intervention simulator."""
from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from components.kpi_cards import render_kpi_cards
from components.executive_sheet import render_executive_sheet
from components.layout import decision_action, page_hero, require_login, section_label
from components.viz_studio import generate_button, graphic_html, render_dynamic_figure, scenario_bar
from services.adapters import get_adapter
from services.decision_brief_service import brief_from_twin
from services.twin_service import run_twin_with_cannibalization
from utils.dmaic_charts import twin_curves

st.set_page_config(page_title="Digital Twin", page_icon="🕹️", layout="wide")
require_login("Digital Twin")

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

section_label("Rival launch (blind spot)")
r1, r2, r3 = st.columns(3)
with r1:
    enable_rival = st.checkbox("Enable competitor launch", True)
with r2:
    rival_month = st.slider("Competitor launch month", 1, months, 3)
with r3:
    default_rival_price = int(
        min(
            float(row["price_psf"]) * 0.92,
            float(upcoming["indicative_price_psf"].min()) if not upcoming.empty else row["price_psf"] * 0.9,
        )
    )
    rival_price = st.number_input("Competitor price ₹/sqft", 4000, 20000, default_rival_price, 100)

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

render_executive_sheet(
    brief_from_twin(
        project=str(project),
        cannibal_loss_cr=float(result.cannibal_loss_cr),
        recovery_cr=float(result.recovery_cr),
        enable_rival=bool(enable_rival),
    ),
    key="twin_eds",
)

section_label("Simulate · regenerate twin curves")
graphic_html("trend-pulse.svg")
view = scenario_bar("twin_view", "Curve focus", ["Full story", "Baseline only", "Rival impact"])
generate_button("twin_studio", "Generate twin graphics")


def _twin_fig():
    # Always keep intervention visible when user moved cut/intervened — demote vs hide
    if view == "Baseline only":
        return twin_curves(result.months, result.baseline, result.baseline, None)
    if view == "Rival impact":
        # Show rival attack + intervention recovery together so sliders still matter
        return twin_curves(result.months, result.baseline, result.intervention, result.cannibalized)
    return twin_curves(result.months, result.baseline, result.intervention, result.cannibalized)


render_dynamic_figure(
    "twin_studio",
    _twin_fig,
    height=420,
    scene=f"{view}|{cut}|{intervene}|{subvention}|{enable_rival}|{rival_month}|{rival_price}",
)

render_kpi_cards(
    [
        {"label": "Baseline revenue", "value": result.revenue_baseline_cr, "format": "cr"},
        {"label": "Under rival attack", "value": result.revenue_cannibal_cr, "format": "cr"},
        {"label": "Blind-spot loss", "value": result.cannibal_loss_cr, "format": "cr"},
        {"label": "Recovery vs rival", "value": result.recovery_cr, "format": "cr"},
    ]
)

decision_action(
    "Prescribe before brochure print",
    [
        f"Blind-spot loss ≈ ₹{result.cannibal_loss_cr} Cr if rival launches unchecked.",
        f"Recovery ≈ ₹{result.recovery_cr} Cr with cut {cut}%{' + subvention' if subvention else ''}.",
        "Lock the winning intervention, then MONITOR on SPC after launch.",
    ],
    tone="warn" if result.cannibal_loss_cr > 0 else "ok",
)
st.info(
    "When a cheaper rival launches, budget buyers divert first, then a share of normal demand. "
    "Prescriptive interventions push recovery while the rival is active."
)
