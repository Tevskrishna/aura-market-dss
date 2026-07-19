"""Forecasting — short-term absorption / booking outlook (IMPROVE)."""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from components.layout import decision_action, page_hero, require_login, section_label
from components.executive_sheet import render_executive_sheet
from services.adapters import get_adapter
from services.data_loader import load_catalog
from services.decision_brief_service import brief_from_forecast
from services.spc_service import forecast_linear_seasonal
from utils.charts import _style

st.set_page_config(page_title="Forecasting", page_icon="🔮", layout="wide")
require_login("Demand Forecast")

page_hero(
    kicker="IMPROVE · Short-horizon predictive",
    title="Forecasting",
    subtitle="6–12 month outlook on sales velocity — aligned to mentor feedback that this tool is strong for near-term decisions.",
    chips=[("Bookings / units", "ok"), ("Confidence bands", ""), ("Not multi-year metro shock model", "warn")],
)

proj = get_adapter().projects()
monthly = load_catalog().get("monthly_absorption")
scope = st.sidebar.radio("Forecast series", ["Market total", "Single project"])
horizon = st.sidebar.slider("Horizon (months)", 3, 12, 6)

if scope == "Single project":
    p = st.sidebar.selectbox("Project", proj["project"].tolist())
    series_df = monthly[monthly["project"] == p].groupby("month", as_index=False)["units_sold_month"].sum()
    title = f"Forecast — {p}"
else:
    series_df = monthly.groupby("month", as_index=False)["units_sold_month"].sum()
    title = "Forecast — market total"

series = series_df.set_index("month")["units_sold_month"]
fc = forecast_linear_seasonal(series, months=horizon)
last = series.index.max()
fc["month"] = pd.date_range(last + pd.offsets.MonthBegin(1), periods=horizon, freq="MS")

render_executive_sheet(
    brief_from_forecast(
        horizon=int(horizon),
        last_yhat=float(fc["forecast"].iloc[-1]) if not fc.empty else 0.0,
        series_label=title,
    ),
    key="fc_eds",
)

section_label(title)
fig = go.Figure()
fig.add_trace(go.Scatter(x=series.index, y=series.values, name="History", line=dict(color="#58a6ff", width=2.5)))
fig.add_trace(go.Scatter(x=fc["month"], y=fc["forecast"], name="Forecast", mode="lines+markers", line=dict(color="#3dd68c", width=2.5)))
fig.add_trace(go.Scatter(x=fc["month"], y=fc["upper"], name="Upper 95%", line=dict(dash="dot", color="#8b949e")))
fig.add_trace(go.Scatter(x=fc["month"], y=fc["lower"], name="Lower 95%", line=dict(dash="dot", color="#8b949e")))
st.plotly_chart(_style(fig, title), width="stretch")
st.dataframe(fc[["month", "forecast", "lower", "upper"]], width="stretch", hide_index=True)

slope = float(fc["forecast"].iloc[-1] - series.iloc[-1]) if len(series) else 0.0
if slope < 0:
    decision_action(
        "Near-term outlook is softening",
        [
            "Pull Digital Twin interventions forward before the next launch quarter.",
            "Reallocate SMC from low-ROI names (Marketing Intelligence) into campaigns that can still book this horizon.",
            "Hold aggressive launch pricing until Competition Intelligence threat is Low/Medium.",
        ],
        tone="warn",
    )
else:
    decision_action(
        "Near-term outlook supports paced growth",
        [
            "Keep MONITOR cadence on SPC; do not overspend SMC without ROI checks.",
            "Use Map DSS top-pick zones for any new land diligence this quarter.",
            "Still clear competition crowding before any price increase.",
        ],
        tone="ok",
    )

st.info(
    "Mentor note: strong for short-term decisions. Longer 1–3 year metro / mega-launch shocks "
    "are Phase-3 — not claimed as complete in this submission build."
)
st.download_button(
    "Download forecast CSV",
    fc.to_csv(index=False).encode("utf-8"),
    file_name="forecast.csv",
    mime="text/csv",
)
