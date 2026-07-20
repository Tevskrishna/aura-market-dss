"""Decision Explanation — why the Hub called GO/HOLD/NO-GO (not a second verdict)."""
from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from components.layout import page_hero, require_login, section_label
from components.executive_sheet import (
    render_executive_sheet,
    render_journey_progress,
    render_open_project_chip,
)
from components.states import empty_state
from services.adapters import get_adapter
from services.competition_service import build_competition_snapshot
from services.decision_brief_service import brief_from_recommendations
from services.decision_context import context_banner_text, get_decision_context
from services.dmaic_service import build_dmaic_snapshot
from services.recommendation_engine import recommendations_for_row
from services.report_service import default_filters
from services.sigma_service import market_kpis
from services.simulation_engine import get_simulation_engine
from utils.dmaic_charts import twin_curves

# Journey label must match DECISION_JOURNEY
MODULE = "Decision Explanation"

st.set_page_config(page_title="Decision Explanation · RealEstateIQ", page_icon="💡", layout="wide")
require_login(MODULE)

ctx = get_decision_context()
df = get_adapter().projects()
if df.empty:
    empty_state(
        "No project catalog",
        "Open Executive Hub after loading data.",
        "Load data/projects.csv",
    )
    st.stop()
projects = df["project"].tolist()

if ctx and ctx.get("project") in projects:
    project = str(ctx["project"])
    st.session_state["recs_project"] = project
else:
    if "recs_project" not in st.session_state:
        st.session_state["recs_project"] = projects[0]
    project = st.selectbox(
        "Project (prefer locking on Executive Hub first)",
        projects,
        key="recs_project",
    )

page_hero(
    kicker="Decision story · Step 9",
    title="Decision Explanation",
    subtitle="Why this recommendation — evidence from the journey, not a second GO / HOLD / NO-GO.",
    compact=True,
)

banner = context_banner_text(ctx)
if banner:
    st.info(banner)
elif not ctx:
    st.warning("Start on Executive Hub — lock project + ₹/sqft so this page explains that call.")

hub_verdict = str(ctx.get("verdict") or "—") if ctx else "—"
hub_risk = ctx.get("threat_score") if ctx else None
st.caption(
    f"Explaining Hub call for **{project}**: **{hub_verdict}**"
    + (f" · Hub risk {hub_risk}/100" if hub_risk is not None else "")
    + " · Final recommendation stays on Executive Hub only."
)

sold_out = df[df["absorption_pct"] >= 95].sort_values("absorption_pct", ascending=False)
row = df[df["project"] == project].iloc[0]
recs = recommendations_for_row(row, sold_out)
total_recover = sum(r["recoverable_units"] for r in recs)

render_journey_progress(MODULE)
render_open_project_chip()
render_executive_sheet(
    brief_from_recommendations(
        project=str(project),
        actions=[f"{r['issue']} → {r['action']}" for r in recs],
        recoverable_units=int(total_recover),
    ),
    key="why_eds",
    mode="why",
)

# --- Evidence story (reuse existing services; no new scoring) ---
section_label("Evidence behind the Hub decision")

mk = market_kpis(df)
try:
    snap = build_competition_snapshot()
except Exception:
    snap = None
try:
    dmaic = build_dmaic_snapshot(default_filters())
except Exception:
    dmaic = None

with st.expander("Market evidence — Is demand healthy?", expanded=True):
    st.write(
        f"Corridor absorption **{mk.get('absorption_pct', 0):.1f}%** · "
        f"unsold pool **{int(mk.get('units_unsold', 0)):,}** · "
        f"at-risk projects **{int(mk.get('at_risk_projects', 0))}**."
    )
    st.caption("Detail lives on Market Intelligence. This page only summarises for the Hub explanation.")

with st.expander("Competition evidence — Will competitors hurt us?", expanded=True):
    if snap is not None:
        st.write(
            f"Upcoming ads **{snap.upcoming_count}** · UC unsold **{snap.unsold_uc_units:,}** · "
            f"RERA projects **{snap.rera_count}**."
        )
        if ctx:
            st.write(
                f"Hub twin lens: blind-spot ≈ **₹{ctx.get('blind_spot_loss_cr', '—')} Cr** · "
                f"recovery ≈ **₹{ctx.get('recovery_cr', '—')} Cr**."
            )
    else:
        st.caption("Competition snapshot unavailable — open Competition & Land for the full layer.")
    st.caption("Land BUY/HOLD/PASS on Competition supports diligence; it does not replace the Hub launch call.")

with st.expander("Buyer evidence — Who will buy?", expanded=False):
    st.write(
        "Buyer Intelligence shows channel mix, demographics, and booking behaviour for the open market. "
        "Use it to confirm the Hub call has a reachable audience — not to invent a new verdict."
    )

with st.expander("Marketing evidence — Can marketing hit the target?", expanded=False):
    st.write(
        "Marketing Intelligence shows SMC spend, ROI quartiles, and weekly allocation. "
        "Weak ROI is a reason the Hub may HOLD — it is not a second launch recommendation."
    )

with st.expander("DMAIC evidence — Why are problems occurring?", expanded=False):
    if dmaic is not None:
        st.write(
            f"Absorption **{float(dmaic.kpis.get('absorption_pct', 0)):.1f}%** · "
            f"at-risk **{int(dmaic.kpis.get('at_risk_projects', 0))}** · "
            f"unsold **{int(dmaic.kpis.get('unsold_units', 0)):,}**."
        )
        st.caption(dmaic.problem_statement[:280] + ("…" if len(dmaic.problem_statement) > 280 else ""))
    else:
        st.caption("Open DMAIC Quality for DEFINE → CONTROL detail.")

with st.expander("Project & twin evidence — Health and what-ifs", expanded=False):
    st.write(
        f"Project row: absorption **{float(row['absorption_pct']):.1f}%** · "
        f"price **₹{float(row['price_psf']):,.0f}/sqft** · "
        f"delay **{float(row.get('construction_delay_months', 0)):.1f} mo**."
    )
    if recs:
        st.markdown("**Rule-engine levers (supporting Hub actions):**")
        for r in recs[:4]:
            st.markdown(f"- **{r['issue']}** → {r['action']} _(~{r['recoverable_units']} units)_")
    else:
        st.success("No material defect signals — Hub MONITOR / current call stands.")

with st.expander("SPC confidence — Can we trust the series?", expanded=False):
    st.write(
        "SPC Control validates whether absorption / booking velocity is statistically stable. "
        "Unstable series = treat Hub intervene plans with caution until special causes are cleared."
    )

st.success(
    f"**These factors support the Executive Hub decision ({hub_verdict}) on {project}.** "
    "Return to Hub for the only final GO / HOLD / NO-GO. Continue → SPC, then Reports for the board pack."
)

with st.expander("Mini digital twin preview (same engine as Hub)", expanded=False):
    price = float(ctx.get("my_price_psf") if ctx and ctx.get("project") == project else row["price_psf"])
    cut_hub = float(ctx.get("cut_pct", 8) if ctx else 8)
    cut = next((r["price_cut_psf"] for r in recs if r.get("price_cut_psf")), 0)
    cut_pct = (cut / row["price_psf"] * 100) if cut else cut_hub
    ticket = float(row["avg_unit_size_sqft"]) * price / 100_000
    twin = get_simulation_engine().run(
        base_monthly_rate=max(int(row["units_sold"] / 24), 6),
        months=int(ctx.get("horizon_months", 12) if ctx else 12),
        price_psf=price,
        construction_progress=float(row["construction_progress_pct"]),
        avg_ticket_lakhs=float(ticket),
        intervene_month=int(ctx.get("intervene_month", 3) if ctx else 3),
        price_cut_pct=float(cut_pct),
        subvention=bool(ctx.get("subvention", True) if ctx else True),
        competitor_launch_month=int(ctx.get("rival_month", 3) if ctx else 3),
    )
    st.plotly_chart(
        twin_curves(twin.months, twin.baseline, twin.intervention, twin.cannibalized),
        width="stretch",
    )
    st.caption(
        f"Recovery ≈ ₹{twin.recovery_cr} Cr · Engine: {get_simulation_engine().name} · "
        "Illustration only — Hub remains the decision."
    )
