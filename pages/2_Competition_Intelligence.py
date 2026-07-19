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
from components.states import data_honesty_banner, page_hub_label
from components.viz_studio import generate_button, live_kpi_strip, render_dynamic_figure, scenario_bar
from config import settings
from services.competition_service import build_competition_snapshot, launch_price_pressure
from services.margin_service import build_margin_viability, evaluate_land_decision, margin_kpis
from utils.charts import PALETTE, _style

st.set_page_config(page_title="Competition & Land · RealEstateIQ", page_icon="🏢", layout="wide")
require_login()

snap = build_competition_snapshot()
margins = build_margin_viability()
mk = margin_kpis(margins)

page_hub_label("Intelligence", "Competition & Land")
data_honesty_banner(
    title="Competition data contract",
    lines=[
        "RERA / upcoming / under-construction / land tables are curated seed CSVs for Bagaluru demo.",
        "Live KRERA / registry adapters are stubbed — do not treat counts as production market truth.",
        "Margin index uses configurable construction cost & FSI load from settings.",
    ],
)

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
live_kpi_strip(
    [
        {"label": "RERA", "display": str(snap.rera_count), "hint": "projects"},
        {"label": "Upcoming", "display": str(snap.upcoming_count), "hint": "ads"},
        {"label": "UC", "display": str(snap.uc_projects), "hint": "sites"},
        {"label": "UC unsold", "display": f"{snap.unsold_uc_units:,}", "hint": "units"},
        {"label": "Avg margin", "display": f"{mk['avg_margin_pct']}%", "hint": "viability"},
    ]
)

section_label("Competition graphics studio")
comp_lens = scenario_bar(
    "comp_lens",
    "Layer",
    ["RERA density", "Upcoming launches", "UC unsold", "Land prices", "Margins"],
)
generate_button("comp_studio", "Generate competition graphics")


def _comp_fig():
    if comp_lens == "RERA density" and not snap.rera.empty:
        tmp = snap.rera.copy()
        tmp["year"] = pd.to_datetime(tmp["approval_date"], errors="coerce").dt.year
        fig = px.bar(tmp.groupby("year").size().reset_index(name="approvals"), x="year", y="approvals", color_discrete_sequence=PALETTE)
        return _style(fig, "RERA approvals by year")
    if comp_lens == "Upcoming launches" and not snap.upcoming.empty:
        fig = px.scatter(
            snap.upcoming,
            x="indicative_price_psf",
            y="planned_units",
            size="planned_units",
            color="developer",
            hover_name="project",
            color_discrete_sequence=PALETTE,
        )
        return _style(fig, "Upcoming competitive launches")
    if comp_lens == "UC unsold" and not snap.under_construction.empty:
        fig = px.bar(
            snap.under_construction.sort_values("unsold_units", ascending=False),
            x="project",
            y="unsold_units",
            color="developer",
            color_discrete_sequence=PALETTE,
        )
        fig.update_layout(xaxis_tickangle=-35)
        return _style(fig, "Under-construction unsold units")
    if comp_lens == "Land prices" and not snap.land.empty:
        fig = px.bar(snap.land.sort_values("land_price_psf"), x="land_price_psf", y="micro_market", orientation="h", color_discrete_sequence=PALETTE)
        return _style(fig, "Land price ₹/sqft")
    if not margins.empty:
        fig = px.bar(
            margins,
            x="margin_pct",
            y="project",
            color="viability",
            orientation="h",
            color_discrete_map={"Viable": "#3dd68c", "Stressed": "#f0b429", "Unviable": "#ff4b4b"},
        )
        return _style(fig, "Developer Margin Viability")
    fig = px.scatter(x=[0], y=[0])
    return _style(fig, "No data for lens")


render_dynamic_figure("comp_studio", _comp_fig, height=400)

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

    section_label("Land decision sheet")
    st.caption("BUY / HOLD / PASS on seed land basis + upcoming/UC pressure — same margin math as Margin tab.")
    mm_opts = snap.land["micro_market"].astype(str).tolist() if not snap.land.empty else [settings.MICRO_MARKET_DEFAULT]
    lc1, lc2 = st.columns([2, 1])
    with lc1:
        land_mm = st.selectbox("Micro-market parcel", mm_opts, key="land_decision_mm")
    with lc2:
        land_exit = st.number_input("Assumed exit ₹/sqft", 5000, 20000, 9000, 100, key="land_decision_exit")
    land_dec = evaluate_land_decision(micro_market=str(land_mm), assumed_sale_psf=float(land_exit))
    render_kpi_cards(
        [
            {"label": "Verdict", "value": land_dec.verdict, "format": "str"},
            {"label": "Margin", "value": land_dec.margin_pct, "format": "pct"},
            {"label": "Land ₹/sqft", "value": land_dec.land_price_psf, "format": "int"},
            {"label": "UC unsold", "value": land_dec.uc_unsold_nearby, "format": "int"},
        ]
    )
    tone = {"BUY": "ok", "HOLD": "warn", "PASS": "warn"}.get(land_dec.verdict, "action")
    decision_action(land_dec.headline, land_dec.actions, tone=tone)
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
