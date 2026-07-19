"""Competition Intelligence — AURA-Market blind spot + margin viability."""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from components.kpi_cards import render_kpi_cards
from components.layout import decision_action, page_hero, require_login, section_label
from services.competition_service import build_competition_snapshot, launch_price_pressure
from services.margin_service import build_margin_viability, margin_kpis
from utils.charts import PALETTE

st.set_page_config(page_title="Competition Intelligence", page_icon="🏢", layout="wide")
require_login()

snap = build_competition_snapshot()
margins = build_margin_viability()
mk = margin_kpis(margins)

page_hero(
    kicker="AURA-Market · Competition blind spot",
    title="Competition Intelligence",
    subtitle="RERA density, pre-launch ads, under-construction supply, land arbitrage, and Developer Margin Viability Index.",
    chips=[
        (f"Adapter · {snap.adapter_mode}", "ok" if snap.adapter_mode == "local" else "warn"),
        ("RERA 3–5 yrs", "ok"),
        ("Coming soon", "ok"),
        ("Margin index", "ok"),
    ],
)

section_label("Supply & land scorecard")
render_kpi_cards(
    [
        {"label": "RERA projects", "value": snap.rera_count, "format": "int"},
        {"label": "Upcoming / advertised", "value": snap.upcoming_count, "format": "int"},
        {"label": "Under construction", "value": snap.uc_projects, "format": "int"},
        {"label": "Unsold UC units", "value": snap.unsold_uc_units, "format": "int"},
        {"label": "Avg margin %", "value": mk["avg_margin_pct"], "format": "pct"},
    ],
    columns=5,
)

t1, t2, t3, t4, t5 = st.tabs(
    ["RERA Pipeline", "Pre-Launch / Coming Soon", "Under Construction", "Land Arbitrage", "Margin Viability"]
)

with t1:
    st.write("Historical + recent RERA clearances — launch density for the micro-market (3–5 year window).")
    st.dataframe(snap.rera, width="stretch", hide_index=True)
    if not snap.rera.empty:
        tmp = snap.rera.copy()
        tmp["year"] = pd.to_datetime(tmp["approval_date"], errors="coerce").dt.year
        fig = px.bar(tmp.groupby("year").size().reset_index(name="approvals"), x="year", y="approvals", color_discrete_sequence=PALETTE)
        st.plotly_chart(fig, width="stretch")

with t2:
    st.write("Early-stage marketing / coming-soon signals — who enters next?")
    st.dataframe(snap.upcoming, width="stretch", hide_index=True)
    if not snap.upcoming.empty:
        fig = px.scatter(
            snap.upcoming,
            x="indicative_price_psf",
            y="planned_units",
            size="planned_units",
            color="developer",
            hover_name="project",
            color_discrete_sequence=PALETTE,
        )
        st.plotly_chart(fig, width="stretch")

with t3:
    st.write("Ongoing supply buyers can choose today.")
    st.dataframe(snap.under_construction, width="stretch", hide_index=True)
    if not snap.under_construction.empty:
        fig = px.bar(
            snap.under_construction.sort_values("unsold_units", ascending=False),
            x="project",
            y="unsold_units",
            color="developer",
            color_discrete_sequence=PALETTE,
        )
        fig.update_layout(xaxis_tickangle=-25)
        st.plotly_chart(fig, width="stretch")

with t4:
    st.write("Raw land cost indices — foundation for margin arbitrage.")
    st.dataframe(snap.land, width="stretch", hide_index=True)
    if not snap.land.empty:
        fig = px.bar(
            snap.land.sort_values("land_price_psf", ascending=False),
            x="micro_market",
            y="land_price_psf",
            color="yoy_change_pct",
            color_continuous_scale="Tealgrn",
        )
        st.plotly_chart(fig, width="stretch")

with t5:
    st.write(
        "Developer Margin Viability Index = (Sale ₹/sqft − loaded land − construction cost) ÷ Sale. "
        "Loaded land uses FSI load factor from config."
    )
    render_kpi_cards(
        [
            {"label": "Viable projects", "value": mk["viable"], "format": "int"},
            {"label": "Stressed", "value": mk["stressed"], "format": "int"},
            {"label": "Unviable", "value": mk["unviable"], "format": "int"},
            {"label": "Avg margin", "value": mk["avg_margin_pct"], "format": "pct"},
        ]
    )
    fig = px.bar(
        margins,
        x="margin_pct",
        y="project",
        color="viability",
        orientation="h",
        color_discrete_map={"Viable": "#3dd68c", "Stressed": "#f0b429", "Unviable": "#ff4b4b"},
    )
    st.plotly_chart(fig, width="stretch")
    st.dataframe(margins, width="stretch", hide_index=True)

section_label("Launch decision helper")
my_price = st.number_input("My planned launch price (₹/sqft)", 5000, 20000, 9000, 100)
threats = launch_price_pressure(snap.upcoming, float(my_price))
if threats.empty:
    st.info("No upcoming rows in current adapter.")
else:
    st.dataframe(threats, width="stretch", hide_index=True)
    high = int((threats["threat"] == "High").sum())
    if high:
        st.warning(f"{high} upcoming project(s) priced within ~5% of your launch price — blind-spot risk.")
        decision_action(
            "Do not launch blind at this price",
            [
                f"{high} upcoming launch(es) sit within ~5% of ₹{my_price:,.0f}/sqft — revise price or differentiate amenity/financing now.",
                "Cross-check UC unsold stock on this page and land margin viability before advertising.",
                "Simulate the rival case on Digital Twin before locking brochure pricing.",
            ],
            tone="warn",
        )
    else:
        st.success("No high-threat price overlap in upcoming set.")
        decision_action(
            "Competition pressure is manageable at this quote",
            [
                "Still monitor RERA density and UC unsold before final print.",
                "Confirm margin stays Viable at this launch price.",
                "Lock MONITOR ownership on SPC after go-live.",
            ],
            tone="ok",
        )
