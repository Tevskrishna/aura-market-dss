"""
AURA-Market — Launch Decision Co-pilot

Product (not a dashboard): one real-world question —
Can I launch / reprice at ₹X this month in Bagaluru?
"""
from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from components.copilot_ui import action_cards, factor_bars, threat_gauge, verdict_banner
from components.layout import require_login, section_label
from components.viz_studio import generate_button, render_dynamic_figure
from config import settings
from services.adapters import get_adapter
from services.launch_copilot_service import evaluate_launch, verdict_markdown
from utils.charts import _style
from utils.dmaic_charts import twin_curves
from services.twin_service import run_twin_with_cannibalization

st.set_page_config(
    page_title="Launch Decision Co-pilot · AURA-Market",
    page_icon=settings.PAGE_ICON,
    layout="wide",
    initial_sidebar_state="collapsed",
)

require_login()
adapter = get_adapter()
projects = adapter.projects()
upcoming = adapter.upcoming()

from components.media import data_uri

_banner = data_uri("hero-bagaluru-day.jpg")
st.html(
    f"""
    <div style="
      position:relative;border-radius:16px;overflow:hidden;margin:0 0 1rem;
      border:1px solid #30363d;min-height:190px;
      background:linear-gradient(100deg,rgba(8,10,14,.88) 20%,rgba(8,10,14,.35) 70%),
                 url('{_banner}') center/cover no-repeat;">
      <div style="padding:1.2rem 1.25rem 1.3rem;max-width:46rem;">
        <div class="dss-kicker">REAL ASSET SURFACE · BAGALURU / AEROSPACE HIGHWAY</div>
        <h1 style="margin:0.2rem 0 0.4rem;color:#fff;">Launch Decision Co-pilot</h1>
        <p style="margin:0;color:#d7dee8;font-size:0.98rem;line-height:1.45;">
          One question builders actually ask: <b>Can I launch at this price this month?</b>
          Move the price slider — threat score and ₹ Cr exposure update live.
        </p>
      </div>
    </div>
    """
)

# --- Controls that recompute in real time on every change ---
c_proj, c_price = st.columns([1.2, 1])
with c_proj:
    project = st.selectbox("My project", projects["project"].tolist(), key="cp_project")
with c_price:
    row0 = projects[projects["project"] == project].iloc[0]
    default_price = int(row0["price_psf"])
    my_price = st.slider(
        "Planned launch / list price (₹/sqft)",
        5000,
        20000,
        default_price,
        50,
        key="cp_price",
    )

a1, a2, a3, a4 = st.columns(4)
with a1:
    cut = st.slider("If I intervene: price cut %", 0, 20, 8, key="cp_cut")
with a2:
    sub = st.toggle("Add subvention", value=True, key="cp_sub")
with a3:
    rival_m = st.slider("Rival launch month", 1, 12, 3, key="cp_rival_m")
with a4:
    months = st.slider("Horizon (months)", 6, 18, 12, key="cp_months")

generate_button("copilot", "Recalculate live verdict")

# Live evaluate on every interaction (slider move = new world state)
verdict = evaluate_launch(
    project=project,
    my_price_psf=float(my_price),
    intervene_cut_pct=float(cut),
    use_subvention=bool(sub),
    rival_month=int(rival_m),
    horizon_months=int(months),
)

left, right = st.columns([1, 1.15])
with left:
    threat_gauge(verdict.threat_score, verdict.verdict, verdict.verdict_color)
    verdict_banner(verdict)
    st.html(
        f"""
        <div class="copilot-loss">
          <div class="copilot-loss-card"><span>Blind-spot loss</span><strong>₹ {verdict.blind_spot_loss_cr}</strong><span>Cr if rival unchecked</span></div>
          <div class="copilot-loss-card"><span>Recovery</span><strong>₹ {verdict.recovery_cr}</strong><span>Cr with your intervene</span></div>
          <div class="copilot-loss-card"><span>Nearest rival</span><strong>₹ {verdict.rival_price_psf:,.0f}</strong><span>{verdict.rival_name}</span></div>
          <div class="copilot-loss-card"><span>Margin</span><strong>{verdict.margin_pct}%</strong><span>{verdict.margin_label}</span></div>
        </div>
        """
    )

with right:
    section_label("Why this score (live factors)")
    factor_bars(verdict)
    section_label("Do this next — 3 actions")
    action_cards(verdict.actions)

section_label("Money path — twin graphic (regenerates with controls)")
row = projects[projects["project"] == project].iloc[0]
ticket = float(row["avg_unit_size_sqft"]) * float(my_price) / 100_000
base_rate = max(int(row["units_sold"] / 24), 6)
twin = run_twin_with_cannibalization(
    base_monthly_rate=base_rate,
    months=int(months),
    price_psf=float(my_price),
    construction_progress=float(row["construction_progress_pct"]),
    avg_ticket_lakhs=ticket,
    intervene_month=4,
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
    height=400,
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
        f"War-room modules (depth): use Modules menu → Competition / Map / SMC. "
        f"Zone tip: **{verdict.zone_tip}** · SMC: {verdict.smc_tip}"
    )

st.markdown(
    f'<p class="dss-footer">Launch Co-pilot · {settings.MICRO_MARKET_DEFAULT} · '
    f"Threat Score is a proprietary composite — not a vanity KPI.</p>",
    unsafe_allow_html=True,
)
