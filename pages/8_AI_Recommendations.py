"""AI Recommendations Engine — Phase-1 Page 4."""
from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from components.layout import page_hero, require_login, section_label
from services.adapters import get_adapter
from services.recommendation_engine import recommendations_for_row
from services.twin_service import run_segmented_twin
from utils.dmaic_charts import twin_curves

st.set_page_config(page_title="AI Recommendations", page_icon="💡", layout="wide")
require_login("AI Recommendations")

page_hero(
    kicker="Phase 1 · IMPROVE (prescribe)",
    title="AI Recommendations Engine",
    subtitle="Rule + ML signals vs sold-out benchmarks — with WHY, expected recoverable units, and mini twin preview.",
    chips=[("6 issue signals", "ok"), ("Benchmarked", ""), ("Mini twin", "")],
)

df = get_adapter().projects()
sold_out = df[df["absorption_pct"] >= 95].sort_values("absorption_pct", ascending=False)

section_label("Sold-out / near sold-out benchmarks")
st.dataframe(
    sold_out[["developer", "project", "absorption_pct", "price_psf", "avg_unit_size_sqft"]],
    width="stretch",
    hide_index=True,
)

project = st.selectbox("Project needing recommendations", df["project"].tolist())
row = df[df["project"] == project].iloc[0]
recs = recommendations_for_row(row, sold_out)

section_label(f"Recommendations for {project}")
total_recover = 0
for r in recs:
    total_recover += r["recoverable_units"]
    with st.container(border=True):
        st.markdown(f"**{r['issue']}** → {r['action']}")
        st.write(r["detail"])
        st.caption(f"Est. recoverable units: {r['recoverable_units']} · Expected impact signal for absorption recovery")

st.metric("Total estimated recoverable units", total_recover)

section_label("Mini digital twin preview")
ticket = row["avg_unit_size_sqft"] * row["price_psf"] / 100_000
cut = next((r["price_cut_psf"] for r in recs if r.get("price_cut_psf")), 0)
cut_pct = (cut / row["price_psf"] * 100) if cut else 8
twin = run_segmented_twin(
    base_monthly_rate=max(int(row["units_sold"] / 24), 6),
    months=12,
    price_psf=float(row["price_psf"]),
    construction_progress=float(row["construction_progress_pct"]),
    avg_ticket_lakhs=float(ticket),
    intervene_month=3,
    price_cut_pct=float(cut_pct),
    subvention=True,
)
st.plotly_chart(twin_curves(twin.months, twin.baseline, twin.intervention, twin.cannibalized), width="stretch")
st.caption(f"Estimated revenue recovery: ₹ {twin.recovery_cr} Cr")
