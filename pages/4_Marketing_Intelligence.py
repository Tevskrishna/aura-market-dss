"""Marketing Intelligence — SMC spend vs outcomes + ROI recommendations."""
from __future__ import annotations

import sys
from pathlib import Path

import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from components.filters import render_global_filters
from components.executive_sheet import render_executive_sheet
from components.kpi_cards import render_kpi_cards
from components.layout import decision_action, page_hero, require_login, section_label
from services.decision_brief_service import brief_from_marketing
from services.marketing_service import build_marketing_insights, weekly_budget_allocation
from utils.charts import marketing_efficiency_chart

st.set_page_config(page_title="Marketing Intelligence", page_icon="📣", layout="wide")
require_login("Marketing Intelligence")

page_hero(
    kicker="MEASURE · Marketing efficiency",
    title="Marketing Intelligence",
    subtitle="SMC spends (₹ Cr) → bookings → ROI quartiles → reallocation actions — stop blind spend.",
    chips=[("SMC workbook", "ok"), ("ROI", "ok"), ("Reallocate", "")],
)

filters = render_global_filters("mkt")
insights = build_marketing_insights(filters)

avg_roi = float(insights.roi["roi_score"].mean()) if not insights.roi.empty else 0.0
cut_n = int((insights.roi["verdict"] == "Cut / reallocate").sum()) if not insights.roi.empty else 0

render_executive_sheet(
    brief_from_marketing(
        total_spend_cr=float(insights.total_spend_cr),
        avg_roi=float(avg_roi),
        cut_n=int(cut_n),
    ),
    key="mktg_eds",
)

section_label("Spend scorecard")
render_kpi_cards(
    [
        {"label": "Total SMC spend", "value": insights.total_spend_cr, "format": "cr"},
        {"label": "Projects tracked", "value": len(insights.by_project), "format": "int"},
        {"label": "Avg ROI score", "value": round(avg_roi, 2), "format": "float"},
        {"label": "Cut candidates", "value": cut_n, "format": "int", "help": "Bottom-quartile ROI"},
    ],
)

if insights.by_quarter.empty:
    st.warning("No marketing spend rows for current filters.")
    st.stop()

decision_action(
    "Reallocate SMC budget this quarter",
    [
        *(f"{r['action']}: {r['project']} — {r['detail']}" for r in insights.reallocation[:4]),
        insights.top_channel_hint or "Protect known high-conversion booking channels when shifting media mix.",
    ],
    tone="action",
)

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

section_label("ROI table (spend → bookings → sales)")
show_cols = [c for c in ["project", "spend_cr", "bookings", "sales_value_cr", "roi_sales", "roi_bookings", "roi_score", "quartile", "verdict"] if c in insights.roi.columns]
st.dataframe(insights.roi[show_cols] if show_cols else insights.roi, width="stretch", hide_index=True)

section_label("Weekly budget allocator")
st.caption("Fixed weekly SMC pool redistributed by ROI quartile (Q1-High gets more; Q4-Low trimmed).")
wb = st.slider("Weekly budget (₹ Cr)", 0.1, 5.0, 1.0, 0.1, key="mkt_weekly_budget")
alloc = weekly_budget_allocation(insights.roi, weekly_budget_cr=float(wb))
if alloc.empty:
    st.info("No ROI rows to allocate.")
else:
    top = alloc.iloc[0]
    decision_action(
        f"Deploy ₹{wb:.1f} Cr this week — lead with {top['project']}",
        [
            f"{r['project']}: ₹{r['allocated_cr']:.2f} Cr ({r['pct_of_budget']:.0f}%) — {r['action']}"
            for _, r in alloc.head(5).iterrows()
        ],
        tone="action",
    )
    st.dataframe(alloc, width="stretch", hide_index=True)
    st.plotly_chart(
        px.bar(
            alloc,
            x="allocated_cr",
            y="project",
            color="quartile",
            orientation="h",
            title=f"Weekly allocation (₹ {wb:.1f} Cr pool)",
        ),
        width="stretch",
    )

section_label("SMC share matrix (utilization)")
if insights.share_long.empty:
    st.caption("No smc_spends.csv share rows loaded.")
else:
    st.caption(f"{len(insights.share_long):,} quarterly share rows from wide SMC workbook — used to cross-check concentration.")
    top_share = (
        insights.share_long.groupby("project", as_index=False)["spend_share"]
        .sum()
        .sort_values("spend_share", ascending=False)
        .head(10)
    )
    st.plotly_chart(
        px.bar(top_share, x="spend_share", y="project", orientation="h", title="Cumulative SMC budget share by project"),
        width="stretch",
    )

c_dl1, c_dl2 = st.columns(2)
with c_dl1:
    st.download_button(
        "Download ROI table",
        insights.roi.to_csv(index=False).encode("utf-8"),
        file_name="marketing_roi.csv",
        mime="text/csv",
        width="stretch",
    )
with c_dl2:
    st.download_button(
        "Download efficiency table",
        insights.efficiency.to_csv(index=False).encode("utf-8"),
        file_name="marketing_efficiency.csv",
        mime="text/csv",
        width="stretch",
    )
