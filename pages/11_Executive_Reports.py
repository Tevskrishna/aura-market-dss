"""Executive Reports — board pack reprints Hub DecisionBrief (Section 0)."""
from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from dataclasses import replace

from components.filters import render_global_filters
from components.executive_sheet import (
    render_executive_sheet,
    render_journey_progress,
    render_open_project_chip,
)
from components.kpi_cards import render_kpi_cards
from components.layout import page_hero, require_login, section_label
from services.competition_service import build_competition_snapshot
from services.decision_brief_service import brief_from_launch
from services.decision_context import (
    context_signature,
    format_relative_age,
    get_decision_context,
    has_decision_context,
    safe_toast,
)
from services.dmaic_service import build_dmaic_snapshot
from components.states import error_state
from services.report_service import (
    build_executive_html,
    build_executive_markdown,
    build_executive_pdf,
    competition_csv,
    resolve_open_launch,
)

st.set_page_config(page_title="Executive Reports", page_icon="📄", layout="wide")
require_login("Reports")

page_hero(
    kicker="Executive decision pack",
    title="Executive Reports",
    subtitle="The business story closes here — not another dashboard. Board pack locked to the Hub call.",
    compact=True,
)

filters = render_global_filters("report")
try:
    md = build_executive_markdown(filters)
    html = build_executive_html(filters)
except Exception as exc:
    error_state("Board pack could not be built", str(exc))
    st.stop()

try:
    pdf_bytes = build_executive_pdf(filters)
    pdf_err = None
except Exception as exc:  # pragma: no cover
    pdf_bytes = b""
    pdf_err = str(exc)

dmaic = build_dmaic_snapshot(filters)
comp = build_competition_snapshot()

try:
    verdict, from_hub = resolve_open_launch()
except Exception as exc:
    error_state("Could not resolve open launch decision", str(exc))
    st.stop()

base_brief = brief_from_launch(verdict)
if from_hub:
    brief = replace(
        base_brief,
        module="Reports",
        next_step=None,
        suggested_actions=[
            "Download PDF board pack — Section 0 matches Hub.",
            "Walk Do this week actions in the IC / mentor review.",
            "Do not claim live KRERA unless AURA_LIVE_*_URL is active.",
        ],
    )
else:
    brief = replace(
        base_brief,
        module="Reports",
        executive_summary=(
            "Using catalog defaults — open Executive Hub to lock today’s call, then regenerate this pack."
        ),
        next_step=None,
        suggested_actions=[
            "Open Executive Hub and set project + ₹/sqft.",
            "Return here — Section 0 will match the Hub verdict.",
            "Download PDF only after the Hub call is locked.",
        ],
    )

ctx = get_decision_context()
age = format_relative_age(ctx.get("updated_at") if ctx else None)
if has_decision_context():
    st.success(
        f"Board pack locked to Hub: {verdict.verdict} · {verdict.project} "
        f"@ ₹{verdict.my_price_psf:,.0f}/sqft · {age}"
    )
    sig = context_signature(ctx)
    if st.session_state.get("_iq_reports_toast_sig") != sig:
        st.session_state["_iq_reports_toast_sig"] = sig
        safe_toast("Board pack matches Hub")
else:
    st.caption(f"Using catalog defaults — open Executive Hub to lock today’s call. ({age})")

render_journey_progress("Reports")
render_open_project_chip()
render_executive_sheet(brief, key="report_eds", mode="board")

section_label("Journey evidence snapshot (for the pack)")
st.caption("Summary figures for the board pack — not a new launch recommendation.")
render_kpi_cards(
    [
        {"label": "Absorption", "value": dmaic.kpis["absorption_pct"], "format": "pct"},
        {"label": "Unsold units", "value": dmaic.kpis["unsold_units"], "format": "int"},
        {"label": "At-risk projects", "value": dmaic.kpis["at_risk_projects"], "format": "int"},
        {"label": "Upcoming launches", "value": comp.upcoming_count, "format": "int"},
        {"label": "UC unsold units", "value": comp.unsold_uc_units, "format": "int"},
    ],
)

section_label("Board pack preview — the business story")
st.caption(
    "Structure: Executive summary → Problem → Evidence → Simulation → Recommendation (Hub) → Action plan → Next steps."
)
st.markdown(md)

st.success(
    "Journey complete — download the pack below. "
    "Section 0 matches today’s Executive Hub GO / HOLD / NO-GO."
)
try:
    from components.ai_copilot import maybe_play_success_chime

    maybe_play_success_chime("ok")
except Exception:
    pass

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
