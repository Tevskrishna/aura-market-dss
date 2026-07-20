"""Scenario Engine — continue Hub decision; NumPy scenario engine (honest)."""
from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from components.kpi_cards import render_kpi_cards
from components.executive_sheet import (
    render_executive_sheet,
    render_journey_progress,
    render_open_project_chip,
)
from components.layout import page_hero, require_login, section_label
from components.states import empty_state
from components.viz_studio import generate_button, graphic_html, render_dynamic_figure, scenario_bar
from services.adapters import get_adapter
from services.decision_brief_service import brief_from_twin
from services.decision_context import context_banner_text, get_decision_context, safe_toast
from services.simulation_engine import get_simulation_engine
from services.twin_service import TWIN_PRESET_NAMES, twin_preset_params
from utils.dmaic_charts import twin_curves

st.set_page_config(page_title="Scenario Engine", page_icon="🕹️", layout="wide")
require_login("Scenario Engine")

ctx = get_decision_context()
PENDING_PRESET = "_pending_twin_preset"

# Apply named preset before widgets mount
if PENDING_PRESET in st.session_state:
    preset_name = st.session_state.pop(PENDING_PRESET)
    months_seed = int(st.session_state.get("twin_months", ctx.get("horizon_months", 12) if ctx else 12))
    params = twin_preset_params(
        preset_name,
        hub_cut=float(ctx.get("cut_pct", 8) if ctx else 8),
        hub_subvention=bool(ctx.get("subvention", True) if ctx else True),
        hub_intervene=int(ctx.get("intervene_month", 4) if ctx else 4),
        hub_rival=int(ctx.get("rival_month", 3) if ctx else 3),
        horizon=months_seed,
    )
    st.session_state["twin_enable_rival"] = params["enable_rival"]
    st.session_state["twin_rival_month"] = params["rival_month"]
    st.session_state["twin_intervene"] = params["intervene_month"]
    st.session_state["twin_cut"] = int(params["cut_pct"])
    st.session_state["twin_subvention"] = params["subvention"]
    st.session_state["twin_preset_label"] = preset_name
    safe_toast(f"Scenario applied: {preset_name}")

# Seed from Hub once per session so CEO does not re-key
if "_twin_ctx_seeded" not in st.session_state and ctx:
    projects_early = get_adapter().projects()["project"].tolist()
    if ctx["project"] in projects_early:
        st.session_state["twin_project"] = ctx["project"]
    st.session_state["twin_months"] = int(ctx.get("horizon_months", 12))
    st.session_state["twin_intervene"] = int(ctx.get("intervene_month", 4))
    st.session_state["twin_cut"] = int(ctx.get("cut_pct", 8))
    st.session_state["twin_subvention"] = bool(ctx.get("subvention", True))
    st.session_state["twin_rival_month"] = int(ctx.get("rival_month", 3))
    st.session_state["twin_enable_rival"] = True
    st.session_state["twin_price"] = float(ctx.get("my_price_psf", 9000))
    st.session_state["_twin_ctx_seeded"] = True

page_hero(
    kicker="What happens if strategy changes?",
    title="Scenario Engine",
    subtitle="Scenario engine (directional ₹ Cr) — price, rival, intervene. Not a city-scale digital twin.",
    compact=True,
)

banner = context_banner_text(ctx)
if banner:
    st.info(banner)
else:
    st.caption("Open Executive Hub first to lock today’s project and price — or set levers below.")

df = get_adapter().projects()
if df.empty:
    empty_state(
        "No projects to simulate",
        "Catalog has no projects — open Executive Hub after seeding data.",
        "Load data/projects.csv or reconnect the adapter.",
    )
    st.stop()

upcoming = get_adapter().upcoming()
projects = df["project"].tolist()
if "twin_project" not in st.session_state:
    st.session_state["twin_project"] = projects[0]
project = st.selectbox("My project", projects, key="twin_project")
row = df[df["project"] == project].iloc[0]

catalog_price = float(row["price_psf"])
if "twin_price" not in st.session_state:
    st.session_state["twin_price"] = catalog_price

section_label("Scenario presets")
pc1, pc2, pc3 = st.columns(3)
for col, name in zip((pc1, pc2, pc3), TWIN_PRESET_NAMES):
    with col:
        if st.button(name, key=f"twin_preset_btn_{name.replace(' ', '_')}", width="stretch"):
            st.session_state[PENDING_PRESET] = name
            st.session_state["twin_preset_label"] = name
            st.rerun()
active_preset = st.session_state.get("twin_preset_label", "Intervene")
st.caption(f"Active scenario: **{active_preset}** · NumPy Poisson engine (illustrative)")

p1, p2 = st.columns(2)
with p1:
    base = st.slider(
        "Base monthly sales rate",
        5,
        80,
        max(int(row["units_sold"] / 24), 8),
        key="twin_base",
    )
with p2:
    if "twin_months" not in st.session_state:
        st.session_state["twin_months"] = 12
    months = st.slider("Simulation duration (months)", 6, 24, key="twin_months")

price_psf = st.number_input(
    "List / launch price ₹/sqft",
    4000,
    20000,
    key="twin_price",
    step=50,
)

if "twin_intervene" not in st.session_state:
    st.session_state["twin_intervene"] = 4
if "twin_cut" not in st.session_state:
    st.session_state["twin_cut"] = 8
if "twin_subvention" not in st.session_state:
    st.session_state["twin_subvention"] = True

intervene = st.slider("My intervention month (0 = none)", 0, months, key="twin_intervene")
cut = st.slider("My price cut %", 0, 20, key="twin_cut")
subvention = st.checkbox("Inject subvention at intervention", key="twin_subvention")

section_label("Rival launch (blind spot)")
r1, r2, r3 = st.columns(3)
with r1:
    if "twin_enable_rival" not in st.session_state:
        st.session_state["twin_enable_rival"] = True
    enable_rival = st.checkbox("Enable competitor launch", key="twin_enable_rival")
with r2:
    if "twin_rival_month" not in st.session_state:
        st.session_state["twin_rival_month"] = 3
    rival_month = st.slider("Competitor launch month", 1, months, key="twin_rival_month")
with r3:
    default_rival_price = int(
        min(
            float(price_psf) * 0.92,
            float(upcoming["indicative_price_psf"].min()) if not upcoming.empty else float(price_psf) * 0.9,
        )
    )
    if "twin_rival_price" not in st.session_state:
        st.session_state["twin_rival_price"] = default_rival_price
    rival_price = st.number_input("Competitor price ₹/sqft", 4000, 20000, key="twin_rival_price", step=100)

ticket = float(row["avg_unit_size_sqft"]) * float(price_psf) / 100_000
result = get_simulation_engine().run(
    base_monthly_rate=base,
    months=months,
    price_psf=float(price_psf),
    construction_progress=float(row["construction_progress_pct"]),
    avg_ticket_lakhs=float(ticket),
    intervene_month=intervene or None,
    price_cut_pct=float(cut),
    subvention=bool(subvention),
    competitor_launch_month=rival_month if enable_rival else None,
    competitor_price_psf=float(rival_price) if enable_rival else None,
)

render_journey_progress("Scenario Engine")
render_open_project_chip()
render_executive_sheet(
    brief_from_twin(
        project=str(project),
        cannibal_loss_cr=float(result.cannibal_loss_cr),
        recovery_cr=float(result.recovery_cr),
        enable_rival=bool(enable_rival),
    ),
    key="twin_eds",
    mode="evidence",
)

section_label("Simulate · regenerate twin curves")
graphic_html("trend-pulse.svg")
view = scenario_bar("twin_view", "Curve focus", ["Full story", "Baseline only", "Rival impact"])
generate_button("twin_studio", "Generate twin graphics")


def _twin_fig():
    from components.visual_experience import try_scenario_month_frames, visual_experience_on

    if view == "Baseline only":
        return twin_curves(result.months, result.baseline, result.baseline, None)
    cann = result.cannibalized if view != "Baseline only" else None
    if visual_experience_on() and view in {"Full story", "Rival impact"}:
        anim = try_scenario_month_frames(
            result.months,
            result.baseline,
            result.intervention,
            result.cannibalized if enable_rival or view == "Rival impact" else cann,
            title="Scenario paths",
        )
        if anim is not None:
            return anim
    return twin_curves(result.months, result.baseline, result.intervention, result.cannibalized)


render_dynamic_figure(
    "twin_studio",
    _twin_fig,
    height=420,
    scene=f"{active_preset}|{view}|{cut}|{intervene}|{subvention}|{enable_rival}|{rival_month}|{rival_price}|{price_psf}",
    visual_purpose="scenario",
)

render_kpi_cards(
    [
        {"label": "Baseline revenue", "value": result.revenue_baseline_cr, "format": "cr"},
        {"label": "Under rival attack", "value": result.revenue_cannibal_cr, "format": "cr"},
        {"label": "Blind-spot loss", "value": result.cannibal_loss_cr, "format": "cr", "help": "₹ Cr at risk if rival launches unchecked"},
        {"label": "Recovery vs rival", "value": result.recovery_cr, "format": "cr", "help": "₹ Cr recoverable with intervene package"},
    ]
)

st.caption(
    f"Engine: {get_simulation_engine().name} (NumPy Poisson scenario — illustrative). "
    "Not SimPy discrete-event. Use EDS Continue → Reports when the ₹ Cr path is clear."
)
