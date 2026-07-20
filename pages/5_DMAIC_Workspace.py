"""DMAIC Workspace shell — DEFINE + MEASURE root-cause views."""
from __future__ import annotations

import sys
from pathlib import Path

import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from components.filters import render_global_filters
from components.executive_sheet import (
    render_executive_sheet,
    render_journey_progress,
    render_open_project_chip,
)
from components.kpi_cards import render_kpi_cards
from components.layout import decision_action, page_hero, require_login, section_label
from services.decision_brief_service import brief_from_dmaic
from services.dmaic_service import build_dmaic_snapshot

st.set_page_config(page_title="DMAIC Workspace", page_icon="🧭", layout="wide")
require_login("DMAIC Quality")

page_hero(
    kicker="Why are problems occurring?",
    title="DMAIC Quality",
    subtitle="Define the unsold defect and measure root causes — operational evidence for the Hub call.",
    compact=True,
)

filters = render_global_filters("dmaic")
snap = build_dmaic_snapshot(filters)

render_journey_progress("DMAIC Quality")
render_open_project_chip()
render_executive_sheet(
    brief_from_dmaic(
        absorption_pct=float(snap.kpis["absorption_pct"]),
        at_risk=int(snap.kpis["at_risk_projects"]),
        unsold=int(snap.kpis["unsold_units"]),
    ),
    key="dmaic_eds",
    mode="evidence",
)

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
        "Take top Pareto projects into Decision Explanation (evidence only — Hub owns GO/HOLD).",
        "Run Scenario Engine interventions (price / subvention) on the largest unsold pile.",
        "Move CONTROL ownership to SPC — review OOC signals monthly.",
    ],
    tone="action",
)

st.caption("Next in the story: Project Deep Dive · Scenario Engine · Decision Explanation · SPC · Reports.")