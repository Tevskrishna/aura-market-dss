"""AURA-Market Home — Predictive & Prescriptive Decision Support System."""
from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from components.layout import info_panel, module_cards, page_hero, require_login, section_label
from config import settings
from services.adapters import get_adapter
from services.data_loader import load_catalog

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

page_hero(
    kicker="Bengaluru Real Estate",
    title="AURA-Market",
    subtitle="AI-powered map & market decision support — Six Sigma DMAIC, ML suitability, competition intelligence, and launch interventions.",
    chips=[
        (f"Signed in · {user.get('name')}", "ok"),
        (f"Data · {meta.mode.upper()}", "ok" if meta.mode == "local" else "warn"),
        ("Systems ready" if ready else "Data blocked", "ok" if ready else "warn"),
    ],
)

c1, c2, c3 = st.columns(3)
with c1:
    info_panel(
        "Problem definition",
        "Developers lose sales when a rival launches next door cheaper — the competition blind spot. "
        "AURA-Market turns diagnostics into predictive + prescriptive simulation.",
    )
with c2:
    info_panel(
        "What AURA-Market does",
        "Track RERA / coming-soon / UC supply, land margin viability, audience demographics, "
        "then simulate cannibalization and intervene before launch.",
    )
with c3:
    info_panel(
        "Data mode",
        f"{meta.description} Live adapters plug in when KRERA/land credentials arrive.",
    )

section_label("Navigate AURA-Market")
module_cards(
    [
        ("01", "Market Overview", "Sigma absorption diagnostics"),
        ("02", "Competition Intelligence", "RERA · Coming soon · UC · Land · Margin index"),
        ("03", "Audience Demographics", "Age · Native · Family · Channels"),
        ("04", "Marketing Intelligence", "SMC spend efficiency"),
        ("05", "DMAIC Workspace", "DEFINE / MEASURE problem framing"),
        ("06", "Builder Deep Dive", "ML forecast + root causes"),
        ("07", "Digital Twin", "Rival cannibalization + interventions"),
        ("08", "AI Recommendations", "Prescriptive actions"),
        ("09", "SPC Control", "CONTROL charts + forecast"),
        ("10", "Map Decision Support", "Where to build — 25 zones"),
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
    f'<p class="dss-footer">{settings.MICRO_MARKET_DEFAULT} · {settings.DEMO_NOTICE}</p>',
    unsafe_allow_html=True,
)
