"""SPC Control Chart — Phase-1 Page 5."""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from components.layout import decision_action, page_hero, require_login, section_label
from services.adapters import get_adapter
from services.data_loader import load_catalog
from services.spc_service import forecast_linear_seasonal, imr_chart
from utils.charts import _style
from utils.dmaic_charts import imr_i_chart, imr_mr_chart

st.set_page_config(page_title="SPC Control Chart", page_icon="📉", layout="wide")
require_login("SPC Control")

page_hero(
    kicker="Phase 1 · CONTROL",
    title="SPC Control Chart (I-MR)",
    subtitle="Six Sigma I-MR · d2=1.128 · Western Electric runs · 6-month forecast with confidence bands.",
    chips=[("OOC >3σ", "ok"), ("Runs rules", ""), ("Forecast", "")],
)

proj = get_adapter().projects()
monthly = load_catalog().get("monthly_absorption")
scope = st.sidebar.radio("Series", ["Market total", "Single project"])
if scope == "Single project":
    p = st.sidebar.selectbox("Project", proj["project"].tolist())
    series_df = monthly[monthly["project"] == p].groupby("month", as_index=False)["units_sold_month"].sum()
else:
    series_df = monthly.groupby("month", as_index=False)["units_sold_month"].sum()

series = series_df.set_index("month")["units_sold_month"]
result = imr_chart(series)
if not result["ok"]:
    st.error(result["reason"])
    st.stop()

section_label("I-Chart")
st.plotly_chart(
    imr_i_chart(series.index, result["x"], result["ucl"], result["lcl"], result["xbar"]),
    width="stretch",
)
section_label("Moving Range")
st.plotly_chart(imr_mr_chart(result["mr"], result["mr_ucl"], result["mrbar"]), width="stretch")
st.write(
    f"σ̂ = MR̄ / d2 = {result['mrbar']:.2f} / 1.128 = **{result['sigma']:.2f}** · "
    f"UCL = {result['ucl']:.1f} · LCL = {result['lcl']:.1f}"
)

section_label("Out-of-control & runs-rule events")
if not result["ooc"]:
    st.success("No OOC / runs-rule violations detected.")
    decision_action(
        "Process appears in statistical control",
        ["Hold the current sales plan; review I-MR monthly; escalate only if a new OOC point appears."],
        tone="ok",
    )
else:
    months = series.index.tolist()
    rows = []
    for e in result["ooc"]:
        idx = e["index"]
        m = months[idx] if idx < len(months) else None
        rows.append(
            {
                "month": m.strftime("%Y-%m") if hasattr(m, "strftime") else str(m),
                "value": e["value"],
                "rule": e["rule"],
                "corrective_action": "Investigate demand/channel shock" if "trend" in e["rule"].lower() or ">" in e["rule"] else "Review pricing & construction messaging",
            }
        )
    st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)
    decision_action(
        "Correct the out-of-control process",
        [f"{r['month']}: {r['corrective_action']} ({r['rule']})" for r in rows[:4]],
        tone="warn",
    )

section_label("6-Month forecast")
fc = forecast_linear_seasonal(series, months=6)
last = series.index.max()
fc["month"] = pd.date_range(last + pd.offsets.MonthBegin(1), periods=6, freq="MS")
fig = go.Figure()
fig.add_trace(go.Scatter(x=series.index, y=series.values, name="History", line=dict(color="#58a6ff")))
fig.add_trace(go.Scatter(x=fc["month"], y=fc["forecast"], name="Forecast", mode="lines+markers", line=dict(color="#3dd68c")))
fig.add_trace(go.Scatter(x=fc["month"], y=fc["upper"], name="Upper 95%", line=dict(dash="dot", color="#8b949e")))
fig.add_trace(go.Scatter(x=fc["month"], y=fc["lower"], name="Lower 95%", line=dict(dash="dot", color="#8b949e")))
st.plotly_chart(_style(fig, "Linear trend + seasonal correction"), width="stretch")
st.dataframe(fc[["month", "forecast", "lower", "upper"]], width="stretch", hide_index=True)
