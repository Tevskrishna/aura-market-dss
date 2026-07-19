"""DMAIC Workspace shell — DEFINE + MEASURE root-cause views."""
from __future__ import annotations

import sys
from pathlib import Path

import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from components.filters import render_global_filters
from components.kpi_cards import render_kpi_cards
from components.layout import decision_action, page_hero, require_login, section_label
from services.dmaic_service import build_dmaic_snapshot

st.set_page_config(page_title="DMAIC Workspace", page_icon="🧭", layout="wide")
require_login()

page_hero(
    kicker="Six Sigma · DEFINE + MEASURE",
    title="DMAIC Workspace",
    subtitle="Frame the unsold-inventory defect, CTQs, Pareto of unsold stock, and at-risk projects. ANALYZE/IMPROVE deepen next.",
    chips=[("DEFINE", "ok"), ("MEASURE", "ok"), ("ANALYZE next", "warn")],
)

filters = render_global_filters("dmaic")
snap = build_dmaic_snapshot(filters)

section_label("Problem statement (DEFINE)")
st.info(snap.problem_statement)

section_label("CTQs")
for ctq in snap.ctqs:
    st.write(f"- {ctq}")

section_label("MEASURE scorecard")
render_kpi_cards(
    [
        {"label": "Absorption", "value": snap.kpis["absorption_pct"], "format": "pct"},
        {"label": "Unsold units", "value": snap.kpis["unsold_units"], "format": "int"},
        {"label": "At-risk projects", "value": snap.kpis["at_risk_projects"], "format": "int"},
        {"label": "Bookings", "value": snap.kpis["bookings"], "format": "int"},
        {"label": "Marketing spend", "value": snap.kpis["marketing_spend_cr"], "format": "cr"},
    ],
    columns=5,
)

section_label("Pareto — unsold units by project")
if snap.pareto.empty:
    st.warning("No inventory rows for filters.")
else:
    fig = px.bar(
        snap.pareto.head(15),
        x="project",
        y="units_unsold",
        color="developer",
        title="Unsold inventory concentration",
    )
    fig.update_layout(xaxis_tickangle=-30)
    st.plotly_chart(fig, width="stretch")
    st.dataframe(snap.pareto, width="stretch", hide_index=True)

section_label("At-risk projects (absorption below threshold)")
st.dataframe(snap.at_risk, width="stretch", hide_index=True)

decision_action(
    "Close the DMAIC loop this sprint",
    [
        "Attack the top Pareto unsold projects with IMPROVE actions on AI Recommendations.",
        "Run Digital Twin interventions (price / subvention) on the largest unsold pile.",
        "Move CONTROL ownership to SPC — review OOC signals monthly.",
    ],
    tone="action",
)

st.caption("ANALYZE/IMPROVE surfaces: Builder Deep Dive · Digital Twin · AI Recommendations · SPC.")