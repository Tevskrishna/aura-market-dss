"""
AURA-Market — Executive Hub (Stitch institutional visual system)

One question: Should we launch / reprice at ₹X this month?
"""
from __future__ import annotations

import sys
import traceback
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config import settings

st.set_page_config(
    page_title="Executive Hub · RealEstateIQ",
    page_icon=settings.PAGE_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
)

try:
    from components.help_kit import HUB_HELP, help_tip
    from components.copilot_ui import action_cards, factor_bars, threat_gauge
    from components.layout import require_login, section_label
    from components.states import empty_state
    from components.stitch_ui import (
        end_stitch_page,
        render_do_this_week,
        render_evidence_vault,
        render_hub_hero,
        render_topbar,
    )
    from components.touch_nav import navigate_to
    from components.viz_studio import render_dynamic_figure
    from services.adapters import get_adapter
    from services.decision_brief_service import weekly_actions_unified
    from services.decision_context import (
        context_signature,
        safe_toast,
        save_decision_context,
    )
    from services.launch_copilot_service import evaluate_launch, verdict_markdown
    from services.simulation_engine import get_simulation_engine
    from utils.charts import _style
    from utils.dmaic_charts import twin_curves
except Exception as boot_err:
    st.error("Hub failed to start — open Manage app → Logs, or share this trace:")
    st.code(f"{type(boot_err).__name__}: {boot_err}\n\n{traceback.format_exc()}")
    st.stop()

# Stitch defaults — calm presentation, no HUD
st.session_state.setdefault("iq_board_mode", True)
st.session_state.setdefault("iq_visual_experience", True)

require_login("Executive Hub")
adapter = get_adapter()
projects = adapter.projects()

if projects.empty:
    empty_state(
        "No projects in catalog",
        "Load data/projects.csv or run PropStack ingest.",
        "Contact admin if this is a tenant workspace.",
    )
    st.stop()

render_topbar()

# Controls first so verdict uses live values — compact Stitch strip
st.html('<div class="st-control-strip">')
c_proj, c_price, c_run = st.columns([1.35, 1.2, 0.75])
with c_proj:
    project = st.selectbox("Project", projects["project"].tolist(), key="cp_project")
with c_price:
    row0 = projects[projects["project"] == project].iloc[0]
    default_price = int(row0["price_psf"])
    my_price = st.slider(
        "Proposed unit price (₹/sqft)",
        5000,
        20000,
        default_price,
        50,
        key="cp_price",
    )
with c_run:
    st.write("")
    st.write("")
    execute = st.button("Execute analysis", type="primary", width="stretch", key="cp_execute")
st.html("</div>")

with st.expander("Stress-test controls", expanded=False):
    a1, a2, a3, a4, a5 = st.columns(5)
    with a1:
        st.slider("Price cut %", 0, 20, 8, key="cp_cut")
    with a2:
        st.toggle("Subvention", value=True, key="cp_sub")
    with a3:
        st.slider("Intervene month", 1, 12, 4, key="cp_intervene_m")
    with a4:
        st.slider("Rival month", 1, 12, 3, key="cp_rival_m")
    with a5:
        st.slider("Horizon (mo)", 6, 18, 12, key="cp_months")

cut = int(st.session_state.get("cp_cut", 8))
sub = bool(st.session_state.get("cp_sub", True))
intervene_m = int(st.session_state.get("cp_intervene_m", 4))
rival_m = int(st.session_state.get("cp_rival_m", 3))
months = int(st.session_state.get("cp_months", 12))

verdict = evaluate_launch(
    project=project,
    my_price_psf=float(my_price),
    intervene_cut_pct=float(cut),
    use_subvention=bool(sub),
    rival_month=int(rival_m),
    horizon_months=int(months),
)

_ctx = save_decision_context(
    project=project,
    my_price_psf=float(my_price),
    cut_pct=float(cut),
    subvention=bool(sub),
    rival_month=int(rival_m),
    intervene_month=int(intervene_m),
    horizon_months=int(months),
    verdict=verdict.verdict,
    threat_score=int(verdict.threat_score),
    blind_spot_loss_cr=float(verdict.blind_spot_loss_cr),
    recovery_cr=float(verdict.recovery_cr),
)
_sig = context_signature(_ctx)
if execute or st.session_state.get("_iq_last_ctx_sig") != _sig:
    st.session_state["_iq_last_ctx_sig"] = _sig
    if execute:
        safe_toast(f"Analysis locked · {verdict.verdict} · {project}")

# —— Stitch first viewport ——
render_hub_hero(
    project=project,
    price_psf=float(my_price),
    verdict=verdict.verdict,
    threat_score=int(verdict.threat_score),
    exposure_cr=float(verdict.blind_spot_loss_cr),
    headline=verdict.headline,
)

st.html('<div class="st-below-hero">')
weekly = weekly_actions_unified(
    launch_actions=list(verdict.actions),
    project=project,
    max_items=5,
)
render_do_this_week(list(weekly[:3]))

with st.expander("Risk detail", expanded=False):
    left, right = st.columns([1, 1.15], gap="large")
    with left:
        threat_gauge(verdict.threat_score, verdict.verdict, verdict.verdict_color)
        st.caption("Launch risk index · 0 clear → 100 abort")
        help_tip("Launch risk index (Threat Score)", key="hub_help_threat", **HUB_HELP["threat_score"])
    with right:
        section_label("Why this score")
        factor_bars(verdict)

render_evidence_vault()
st.html('<div class="st-vault-wrap">')
ev1, ev2, ev3, ev4 = st.columns(4)
with ev1:
    if st.button("Open Market →", width="stretch", key="hub_ev_mkt"):
        navigate_to("Market Intelligence", "pages/1_Market_Overview.py")
with ev2:
    if st.button("Open Competition →", width="stretch", key="hub_ev_comp"):
        navigate_to("Competition & Land", "pages/2_Competition_Intelligence.py")
with ev3:
    if st.button("Open Scenario →", width="stretch", key="hub_ev_twin"):
        navigate_to("Scenario Engine", "pages/7_Digital_Twin.py")
with ev4:
    if st.button("Open Reports →", width="stretch", key="hub_ev_rep"):
        navigate_to("Reports", "pages/11_Executive_Reports.py")
st.html("</div>")

with st.expander("Analyst tools · scenario ₹ Cr · download", expanded=False):
    row = projects[projects["project"] == project].iloc[0]
    ticket = float(row["avg_unit_size_sqft"]) * float(my_price) / 100_000
    base_rate = max(int(row["units_sold"] / 24), 6)
    twin = get_simulation_engine().run(
        base_monthly_rate=base_rate,
        months=int(months),
        price_psf=float(my_price),
        construction_progress=float(row["construction_progress_pct"]),
        avg_ticket_lakhs=ticket,
        intervene_month=int(intervene_m),
        price_cut_pct=float(cut),
        subvention=bool(sub),
        competitor_launch_month=int(rival_m),
        competitor_price_psf=float(verdict.rival_price_psf),
    )
    render_dynamic_figure(
        "copilot",
        lambda: _style(
            twin_curves(twin.months, twin.baseline, twin.intervention, twin.cannibalized),
            f"{project} · ₹{my_price:,.0f}/sqft · {verdict.verdict}",
        ),
        height=340,
        scene=f"{project}|{my_price}|{cut}|{sub}|{intervene_m}|{rival_m}|{months}",
        visual_purpose="scenario",
    )
    action_cards(weekly[:3])
    md = verdict_markdown(verdict)
    st.download_button(
        "Download verdict (.md)",
        md.encode("utf-8"),
        file_name=f"launch_verdict_{project.replace(' ', '_')}.md",
        mime="text/markdown",
        width="stretch",
    )
    st.caption(f"{settings.MICRO_MARKET_DEFAULT} · PropStack Dec 2022 – Nov 2025")

st.html("</div>")
end_stitch_page("Executive Hub")
