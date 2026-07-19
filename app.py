"""AURA-Market Home — proptech decision cockpit (dynamic UI)."""
from __future__ import annotations

import sys
from pathlib import Path

import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from components.layout import decision_action, module_cards, require_login, section_label
from components.viz_studio import (
    cockpit_hero,
    generate_button,
    live_kpi_strip,
    render_dynamic_figure,
    scenario_bar,
)
from config import settings
from services.adapters import get_adapter
from services.data_loader import load_catalog
from services.map_service import map_home_kpis, scored_zones
from services.market_service import build_market_bundle
from services.sigma_service import market_kpis
from models.market import FilterState
from datetime import date
from utils.charts import PALETTE, _style

st.set_page_config(
    page_title=settings.APP_SHORT_NAME,
    page_icon=settings.PAGE_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
)

user = require_login()
adapter = get_adapter()
meta = adapter.meta()
catalog = load_catalog()
report = catalog.report
ready = bool(report and report.ready_for_market_overview)

zones = scored_zones()
mk = map_home_kpis(zones)
filters = FilterState(
    builder=settings.ALL_BUILDERS_LABEL,
    project=settings.ALL_PROJECTS_LABEL,
    date_start=date(2022, 12, 1),
    date_end=date(2025, 11, 30),
    quarter=settings.ALL_QUARTERS_LABEL,
)
bundle = build_market_bundle(filters, catalog)
sk = market_kpis(bundle.projects)

cockpit_hero(
    title="AURA-Market",
    subtitle="Interactive Bengaluru micro-market DSS — click scenarios to regenerate live graphics, then act.",
    bullets=[
        "Map-first location scoring (proptech pattern: decide WHERE before price)",
        "Competition + SMC ROI signals that update on demand",
        "Digital Twin interventions before you publish a launch price",
    ],
)

live_kpi_strip(
    [
        {"label": "Absorption", "display": f"{sk['absorption_pct']}%", "hint": "Bagaluru filtered"},
        {"label": "At-risk", "display": str(sk["at_risk_projects"]), "hint": "<70% absorption"},
        {"label": "Zones", "display": str(mk["areas_covered"]), "hint": "Suitability scored"},
        {"label": "AI top pick", "display": str(mk["ai_top_pick"]), "hint": "Where to diligence"},
        {"label": "Data", "display": meta.mode.upper(), "hint": user.get("name", "user")},
        {"label": "Ready", "display": "YES" if ready else "NO", "hint": "Catalog gate"},
    ]
)

decision_action(
    "Lead walkthrough — 6 minutes",
    [
        "Home studio (below): pick a scenario → Generate live graphics.",
        "Competition Intelligence: launch price helper.",
        "Marketing Intelligence: cut/boost ROI actions.",
        "Digital Twin → Map Decision Support → download Executive Report.",
    ],
)

section_label("Live graphics studio")
scene = scenario_bar(
    "home_scene",
    "Market lens",
    ["Absorption health", "Price vs sell-through", "Zone suitability", "Growth corridors"],
)
focus = scenario_bar(
    "home_focus",
    "Segment focus",
    ["All builders", "At-risk only", "Sold-out benchmarks"],
)
generate_button("home_studio", "Generate responsive graphics")

projects = bundle.projects.copy()
if focus == "At-risk only":
    projects = projects[projects["absorption_pct"] < 70]
elif focus == "Sold-out benchmarks":
    projects = projects[projects["absorption_pct"] >= 95]


def _home_fig():
    if scene == "Absorption health":
        fig = px.bar(
            projects.sort_values("absorption_pct"),
            x="project",
            y="absorption_pct",
            color="absorption_pct",
            color_continuous_scale=["#ff4b4b", "#f0b429", "#3dd68c"],
            title=f"Absorption % · {focus}",
        )
        fig.update_layout(xaxis_tickangle=-35)
        return _style(fig, "Live absorption surface")
    if scene == "Price vs sell-through":
        fig = px.scatter(
            projects,
            x="price_psf",
            y="absorption_pct",
            size="total_units",
            color="developer",
            hover_name="project",
            color_discrete_sequence=PALETTE,
            title="Price positioning vs absorption",
        )
        return _style(fig, "Price vs sell-through")
    if scene == "Zone suitability":
        fig = px.bar(
            zones.sort_values("suitability_score", ascending=False).head(12),
            x="suitability_score",
            y="zone",
            orientation="h",
            color="suitability_score",
            color_continuous_scale=["#ff4b4b", "#f0b429", "#3dd68c"],
            title="Top construction-ready zones",
        )
        return _style(fig, "Zone suitability")
    fig = px.scatter(
        zones,
        x="metro_km",
        y="price_trend_yoy_pct",
        size="population_growth_index",
        color="suitability_score",
        hover_name="zone",
        color_continuous_scale="Turquoise",
        title="Growth corridors · metro distance vs YoY price",
    )
    return _style(fig, "Growth corridors")


render_dynamic_figure("home_studio", _home_fig, height=420)

section_label("Navigate AURA-Market")
module_cards(
    [
        ("01", "Market Overview", "Sigma absorption diagnostics"),
        ("02", "Competition Intelligence", "RERA · Coming soon · UC · Land · Margin index"),
        ("03", "Audience Demographics", "Age · Native · Family · Channels"),
        ("04", "Marketing Intelligence", "SMC spend → ROI → reallocate"),
        ("05", "DMAIC Workspace", "DEFINE / MEASURE problem framing"),
        ("06", "Builder Deep Dive", "ML forecast + root causes"),
        ("07", "Digital Twin", "Rival cannibalization + interventions"),
        ("08", "AI Recommendations", "Prescriptive actions"),
        ("09", "SPC Control", "CONTROL charts + forecast"),
        ("10", "Map Decision Support", "Where to build — interactive map"),
        ("11", "Executive Reports", "Downloadable decision brief"),
        ("12", "Forecasting", "Short-horizon predictive outlook"),
    ]
)

section_label("Dataset readiness")
rows = [
    {
        "Dataset": d.name.replace("_", " ").title(),
        "Status": "OK" if d.ok else "FAIL",
        "Rows": f"{d.rows:,}",
        "Notes": "; ".join([*d.errors, *d.warnings]) or "—",
    }
    for d in (report.datasets if report else [])
]
st.dataframe(rows, width="stretch", hide_index=True)

st.markdown(
    f'<p class="dss-footer">{settings.MICRO_MARKET_DEFAULT} · Dynamic UI rebuild · {settings.DEMO_NOTICE}</p>',
    unsafe_allow_html=True,
)
