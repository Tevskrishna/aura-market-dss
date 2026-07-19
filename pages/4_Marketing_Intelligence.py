"""Marketing Intelligence — SMC spend vs outcomes."""
from __future__ import annotations

import sys
from pathlib import Path

import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from components.filters import render_global_filters
from components.kpi_cards import render_kpi_cards
from components.layout import page_hero, require_login, section_label
from services.marketing_service import build_marketing_insights
from utils.charts import marketing_efficiency_chart

st.set_page_config(page_title="Marketing Intelligence", page_icon="📣", layout="wide")
require_login()

page_hero(
    kicker="MEASURE · Marketing efficiency",
    title="Marketing Intelligence",
    subtitle="SMC spends (₹ Cr) linked to bookings and sales outcomes — stop blind spend.",
    chips=[("SMC workbook", "ok"), ("Quarterly", ""), ("Efficiency", "")],
)

filters = render_global_filters("mkt")
insights = build_marketing_insights(filters)

section_label("Spend scorecard")
render_kpi_cards(
    [
        {"label": "Total SMC spend", "value": insights.total_spend_cr, "format": "cr"},
        {"label": "Projects tracked", "value": len(insights.by_project), "format": "int"},
        {"label": "Quarters", "value": len(insights.by_quarter), "format": "int"},
    ],
    columns=3,
)

if insights.by_quarter.empty:
    st.warning("No marketing spend rows for current filters.")
    st.stop()

st.plotly_chart(
    px.line(insights.by_quarter, x="fy_quarter", y="spend_cr", markers=True, title="SMC spend by quarter (₹ Cr)"),
    width="stretch",
)

c1, c2 = st.columns(2)
with c1:
    st.plotly_chart(
        px.bar(
            insights.by_project.head(12),
            x="spend_cr",
            y="project",
            orientation="h",
            title="Spend by project",
        ),
        width="stretch",
    )
with c2:
    st.plotly_chart(marketing_efficiency_chart(insights.efficiency), width="stretch")

st.dataframe(insights.efficiency, width="stretch", hide_index=True)
st.download_button(
    "Download efficiency table",
    insights.efficiency.to_csv(index=False).encode("utf-8"),
    file_name="marketing_efficiency.csv",
    mime="text/csv",
)
