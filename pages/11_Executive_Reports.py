"""Executive Reports — downloadable decision brief for company submission."""
from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from components.filters import render_global_filters
from components.layout import page_hero, require_login, section_label
from services.report_service import build_executive_markdown
from services.competition_service import build_competition_snapshot
from services.dmaic_service import build_dmaic_snapshot
from components.kpi_cards import render_kpi_cards

st.set_page_config(page_title="Executive Reports", page_icon="📄", layout="wide")
require_login()

page_hero(
    kicker="CONTROL · Submission pack",
    title="Executive Reports",
    subtitle="One-click decision brief for mentors and company reviewers — sourced only from shared services.",
    chips=[("Markdown export", "ok"), ("Filter-aware", ""), ("Company walkthrough", "")],
)

filters = render_global_filters("report")
md = build_executive_markdown(filters)
dmaic = build_dmaic_snapshot(filters)
comp = build_competition_snapshot()

section_label("Brief scorecard")
render_kpi_cards(
    [
        {"label": "Absorption", "value": dmaic.kpis["absorption_pct"], "format": "pct"},
        {"label": "Unsold units", "value": dmaic.kpis["unsold_units"], "format": "int"},
        {"label": "At-risk projects", "value": dmaic.kpis["at_risk_projects"], "format": "int"},
        {"label": "Upcoming launches", "value": comp.upcoming_count, "format": "int"},
        {"label": "UC unsold units", "value": comp.unsold_uc_units, "format": "int"},
    ],
    columns=5,
)

section_label("Preview")
st.markdown(md)

st.download_button(
    "Download executive brief (.md)",
    data=md.encode("utf-8"),
    file_name="bagaluru_executive_brief.md",
    mime="text/markdown",
    width="stretch",
)
