"""AI Recommendations — continue Hub project; prescribe with mini twin."""
from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from components.layout import page_hero, require_login, section_label
from components.executive_sheet import render_executive_sheet
from components.states import empty_state
from services.adapters import get_adapter
from services.decision_brief_service import brief_from_recommendations
from services.decision_context import context_banner_text, get_decision_context
from services.recommendation_engine import recommendations_for_row
from services.simulation_engine import get_simulation_engine
from utils.dmaic_charts import twin_curves

st.set_page_config(page_title="AI Recommendations", page_icon="💡", layout="wide")
require_login("AI Recommendations")

ctx = get_decision_context()
df = get_adapter().projects()
if df.empty:
    empty_state(
        "No projects for recommendations",
        "Seed catalog missing — open Executive Hub after loading data.",
        "Load data/projects.csv",
    )
    st.stop()
projects = df["project"].tolist()

if "_recs_ctx_seeded" not in st.session_state and ctx and ctx.get("project") in projects:
    st.session_state["recs_project"] = ctx["project"]
    st.session_state["_recs_ctx_seeded"] = True
if "recs_project" not in st.session_state:
    st.session_state["recs_project"] = projects[0]

page_hero(
    kicker="IMPROVE · Prescribe",
    title="AI Recommendations",
    subtitle="Actions for the open project — why, recoverable units, mini twin.",
    compact=True,
)

banner = context_banner_text(ctx)
if banner:
    st.info(banner)

sold_out = df[df["absorption_pct"] >= 95].sort_values("absorption_pct", ascending=False)

section_label("Sold-out / near sold-out benchmarks")
st.dataframe(
    sold_out[["developer", "project", "absorption_pct", "price_psf", "avg_unit_size_sqft"]],
    width="stretch",
    hide_index=True,
)

project = st.selectbox("Project needing recommendations", projects, key="recs_project")
row = df[df["project"] == project].iloc[0]
recs = recommendations_for_row(row, sold_out)

total_recover = sum(r["recoverable_units"] for r in recs)
render_executive_sheet(
    brief_from_recommendations(
        project=str(project),
        actions=[f"{r['issue']} → {r['action']}" for r in recs],
        recoverable_units=int(total_recover),
    ),
    key="recs_eds",
)

section_label(f"Recommendations for {project}")
for r in recs:
    with st.container(border=True):
        st.markdown(f"**{r['issue']}** → {r['action']}")
        st.write(r["detail"])
        st.caption(f"Est. recoverable units: {r['recoverable_units']} · Expected impact signal for absorption recovery")

st.metric("Total estimated recoverable units", total_recover)

section_label("Mini digital twin preview")
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
st.plotly_chart(twin_curves(twin.months, twin.baseline, twin.intervention, twin.cannibalized), width="stretch")
st.caption(
    f"Estimated revenue recovery: ₹ {twin.recovery_cr} Cr · Same engine as Hub ("
    f"{get_simulation_engine().name}). Continue → Digital Twin to stress-test. "
    "Hub 'Do this week' already merges these prescribe lines."
)
