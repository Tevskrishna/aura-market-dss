"""Executive Reports — downloadable decision brief for company submission."""
from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from components.filters import render_global_filters
from components.kpi_cards import render_kpi_cards
from components.layout import decision_action, page_hero, require_login, section_label
from services.competition_service import build_competition_snapshot
from services.dmaic_service import build_dmaic_snapshot
from services.report_service import (
    build_executive_html,
    build_executive_markdown,
    build_executive_pdf,
    competition_csv,
)

st.set_page_config(page_title="Executive Reports", page_icon="📄", layout="wide")
require_login("Reports")

page_hero(
    kicker="CONTROL · Submission pack",
    title="Executive Reports",
    subtitle="One-click board pack for mentors and reviewers — Markdown, printable HTML, and native PDF.",
    chips=[("Markdown", "ok"), ("HTML", "ok"), ("PDF board pack", "ok")],
)

filters = render_global_filters("report")
md = build_executive_markdown(filters)
html = build_executive_html(filters)
try:
    pdf_bytes = build_executive_pdf(filters)
    pdf_err = None
except Exception as exc:  # pragma: no cover
    pdf_bytes = b""
    pdf_err = str(exc)
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
)

decision_action(
    "Use this brief in the review meeting",
    [
        "Download the PDF board pack for mentors who want a single attachment.",
        "Walk Priority actions first — then attach Marketing allocator and Competition land sheet.",
        "Do not claim live KRERA — state local/seed competition mode unless credentials arrive.",
    ],
)

section_label("Preview")
st.markdown(md)

c1, c2 = st.columns(2)
c3, c4 = st.columns(2)
with c1:
    st.download_button(
        "Download brief (.md)",
        data=md.encode("utf-8"),
        file_name="aura_executive_brief.md",
        mime="text/markdown",
        width="stretch",
    )
with c2:
    st.download_button(
        "Download printable HTML",
        data=html.encode("utf-8"),
        file_name="aura_executive_brief.html",
        mime="text/html",
        width="stretch",
    )
with c3:
    if pdf_bytes:
        st.download_button(
            "Download board pack (PDF)",
            data=pdf_bytes,
            file_name="aura_board_pack.pdf",
            mime="application/pdf",
            width="stretch",
        )
    else:
        st.warning(pdf_err or "PDF unavailable — install fpdf2.")
with c4:
    st.download_button(
        "Download competition CSV",
        data=competition_csv().to_csv(index=False).encode("utf-8"),
        file_name="competition_upcoming.csv",
        mime="text/csv",
        width="stretch",
    )
