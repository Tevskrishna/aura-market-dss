"""Builder Deep Dive — Phase-1 Page 2."""
from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from components.kpi_cards import render_kpi_cards
from components.layout import decision_action, page_hero, require_login, section_label
from services.adapters import get_adapter
from services.recommendation_engine import (
    defect_probability,
    fit_gb_forecast,
    gb_artifact_status,
    recommendations_for_row,
    root_causes,
)
from services.sigma_service import market_kpis
from utils.dmaic_charts import ml_vs_actual_chart, stacked_sold_unsold

st.set_page_config(page_title="Builder Deep Dive", page_icon="🏗️", layout="wide")
require_login("Project Deep Dive")

page_hero(
    kicker="Phase 1 · ANALYZE",
    title="Builder Deep Dive",
    subtitle="Per-developer KPIs, sold vs unsold stack, Gradient Boosting absorption forecast, and at-risk root causes.",
    chips=[("ML forecast", "ok"), ("Defect probability", ""), ("Root causes", "")],
)

df = get_adapter().projects()
developer = st.sidebar.selectbox("Developer", sorted(df["developer"].unique()))
sub = df[df["developer"] == developer].copy()
k = market_kpis(sub)

section_label(f"{developer} scorecard")
render_kpi_cards(
    [
        {"label": "Total units", "value": k["total_units"], "format": "int"},
        {"label": "Sold %", "value": k["absorption_pct"], "format": "pct"},
        {"label": "Unsold", "value": k["units_unsold"], "format": "int"},
        {"label": "Avg delay (mo)", "value": round(float(sub["construction_delay_months"].mean()), 1), "format": "float"},
    ]
)

st.plotly_chart(stacked_sold_unsold(sub), width="stretch")

section_label("Gradient Boosting — forecast vs actual")
force = st.checkbox("Force retrain model", value=False, help="Ignore cached artifact under models/artifacts/")
pred, score, _ = fit_gb_forecast(df, force_retrain=force)
status = gb_artifact_status()
loaded = bool(getattr(pred, "attrs", {}).get("model_loaded_from_disk"))
st.caption(
    f"Holdout R² ≈ {score:.2f} · "
    + ("loaded from disk artifact" if loaded else "trained and saved this run")
    + (f" · `{status['path']}`" if status.get("path") else "")
)
pred_sub = pred[pred["developer"] == developer]
st.plotly_chart(ml_vs_actual_chart(pred_sub), width="stretch")

section_label("At-risk project cards")
at_risk = sub[sub["absorption_pct"] < 85].sort_values("absorption_pct")
sold_out = df[df["absorption_pct"] >= 95]
if at_risk.empty:
    st.success("No projects under 85% absorption for this builder.")
    decision_action(
        "Hold the playbook",
        ["Keep price discipline; pace construction CRM updates; re-check monthly on SPC."],
        tone="ok",
    )
else:
    decision_action(
        f"Execute IMPROVE actions for {developer}",
        [
            "Open each at-risk expander below — run the listed actions this fortnight.",
            "Validate material price cuts on Digital Twin before publishing ads.",
            "Track recovery on Market Overview absorption bands next review.",
        ],
        tone="warn",
    )
    for _, row in at_risk.iterrows():
        with st.expander(f"{row['project']} — {row['absorption_pct']}% absorbed"):
            st.write(f"**ML defect probability:** {defect_probability(row):.0%}")
            st.write("**Root causes:**")
            for c in root_causes(row):
                st.write(f"- {c}")
            st.write("**Developer actions:**")
            for rec in recommendations_for_row(row, sold_out)[:3]:
                st.write(f"- **{rec['action']}** — {rec['detail']} (est. recoverable {rec['recoverable_units']} units)")
