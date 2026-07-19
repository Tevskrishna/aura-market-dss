"""
AURA-Market — Launch Decision Co-pilot (v1 polish: CEO 10-second Hub)

One question: Should we launch / reprice at ₹X this month?
"""
from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from components.copilot_ui import action_cards, factor_bars, threat_gauge
from components.executive_sheet import render_executive_sheet
from components.layout import require_login, section_label
from components.states import data_honesty_banner, empty_state, page_hub_label
from components.touch_nav import render_touch_hub
from components.viz_studio import render_dynamic_figure
from config import settings
from services.adapters import get_adapter
from services.decision_brief_service import brief_from_launch
from services.decision_context import (
    context_signature,
    format_relative_age,
    get_decision_context,
    safe_toast,
    save_decision_context,
)
from services.launch_copilot_service import evaluate_launch, verdict_markdown
from services.twin_service import run_twin_with_cannibalization
from utils.charts import _style
from utils.dmaic_charts import twin_curves

st.set_page_config(
    page_title="Executive Hub · RealEstateIQ",
    page_icon=settings.PAGE_ICON,
    layout="wide",
    initial_sidebar_state="collapsed",
)

require_login("Executive Hub")
adapter = get_adapter()
projects = adapter.projects()

page_hub_label("RealEstateIQ", "Executive Hub")
data_honesty_banner()

if projects.empty:
    empty_state(
        "No projects in catalog",
        "Load data/projects.csv or run seed scripts.",
        "Contact admin if this is a tenant workspace.",
    )
    st.stop()

# Freshness for status strip (updated after save below)
_prior = get_decision_context()
_fresh = format_relative_age(_prior.get("updated_at") if _prior else None)

st.html(
    f"""
    <div class="iq-live-strip" aria-live="polite">
      <span class="iq-live-dot" aria-hidden="true"></span>
      <span class="iq-live-label">Decision intelligence · Bagaluru</span>
      <span class="iq-live-meta">{_fresh} · Aerospace Highway</span>
    </div>
    <div class="iq-hub-ask" role="heading" aria-level="1">
      <div class="iq-hub-ask-kicker">Executive decision · Launch call</div>
      <h1>Should we launch at this price?</h1>
      <p>Set project and ₹/sqft. Verdict, risk, and ₹ Cr exposure update with your open decision — carried into Twin and the board pack.</p>
    </div>
    """
)

c_proj, c_price = st.columns([1.2, 1])
with c_proj:
    project = st.selectbox("Project", projects["project"].tolist(), key="cp_project")
with c_price:
    row0 = projects[projects["project"] == project].iloc[0]
    default_price = int(row0["price_psf"])
    my_price = st.slider(
        "Launch / list price (₹/sqft)",
        5000,
        20000,
        default_price,
        50,
        key="cp_price",
    )

with st.expander("Stress-test controls (cut · rival · horizon)", expanded=False):
    a1, a2, a3, a4, a5 = st.columns(5)
    with a1:
        cut = st.slider("Price cut %", 0, 20, 8, key="cp_cut")
    with a2:
        sub = st.toggle("Subvention", value=True, key="cp_sub")
    with a3:
        intervene_m = st.slider("Intervene month", 1, 12, 4, key="cp_intervene_m")
    with a4:
        rival_m = st.slider("Rival month", 1, 12, 3, key="cp_rival_m")
    with a5:
        months = st.slider("Horizon (mo)", 6, 18, 12, key="cp_months")

# Defaults if expander never opened still need variables — sliders keep session state
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

# Carry open decision into Twin / Recs / Board pack (CEO morning loop)
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
if st.session_state.get("_iq_last_ctx_sig") != _sig:
    st.session_state["_iq_last_ctx_sig"] = _sig
    safe_toast(f"Open decision locked · {verdict.verdict} · {project}")

# --- Decision story (primary) ---
render_executive_sheet(brief_from_launch(verdict), key="hub_eds")

left, right = st.columns([1, 1.15], gap="large")
with left:
    threat_gauge(verdict.threat_score, verdict.verdict, verdict.verdict_color)
    st.html(
        f"""
        <div class="copilot-loss">
          <div class="copilot-loss-card"><span>Blind-spot loss</span><strong>₹ {verdict.blind_spot_loss_cr}</strong><span>Cr if rival unchecked</span></div>
          <div class="copilot-loss-card"><span>Recovery</span><strong>₹ {verdict.recovery_cr}</strong><span>Cr with intervene</span></div>
          <div class="copilot-loss-card"><span>Nearest rival</span><strong>₹ {verdict.rival_price_psf:,.0f}</strong><span>{verdict.rival_name}</span></div>
          <div class="copilot-loss-card"><span>Margin</span><strong>{verdict.margin_pct}%</strong><span>{verdict.margin_label}</span></div>
        </div>
        """
    )
with right:
    section_label("Why this score")
    factor_bars(verdict)
    section_label("Do this week")
    action_cards(verdict.actions[:3])

# --- Supporting evidence (secondary) ---
row = projects[projects["project"] == project].iloc[0]
ticket = float(row["avg_unit_size_sqft"]) * float(my_price) / 100_000
base_rate = max(int(row["units_sold"] / 24), 6)
twin = run_twin_with_cannibalization(
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

with st.expander("₹ Cr money path (digital twin)", expanded=True):
    render_dynamic_figure(
        "copilot",
        lambda: _style(
            twin_curves(twin.months, twin.baseline, twin.intervention, twin.cannibalized),
            f"{project} · ₹{my_price:,.0f}/sqft · {verdict.verdict}",
        ),
        height=360,
        scene=f"{project}|{my_price}|{cut}|{sub}|{intervene_m}|{rival_m}|{months}",
    )

md = verdict_markdown(verdict)
d1, d2 = st.columns(2)
with d1:
    st.download_button(
        "Download verdict (.md)",
        md.encode("utf-8"),
        file_name=f"launch_verdict_{project.replace(' ', '_')}.md",
        mime="text/markdown",
        width="stretch",
    )
with d2:
    st.caption(
        f"{settings.MICRO_MARKET_DEFAULT} · Zone: {verdict.zone_tip} · {verdict.smc_tip}"
    )

with st.expander("Evidence workspaces (optional depth)", expanded=False):
    st.caption("Use after the launch call is clear — Competition, Twin, Map, Reports.")
    render_touch_hub(title="Open a workspace")

st.markdown(
    f'<p class="dss-footer">Launch Co-pilot · Threat Score is a proprietary composite — not a vanity KPI.</p>',
    unsafe_allow_html=True,
)
