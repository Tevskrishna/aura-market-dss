"""DMAIC / Market Overview Plotly charts (Phase-1 visual contract)."""
from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from utils.charts import PALETTE, _style, _empty


def absorption_band_chart(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return _empty("No projects")
    out = df.copy()
    out["band"] = out["absorption_pct"].apply(
        lambda x: "Red <70%" if x < 70 else ("Yellow 70–95%" if x < 95 else "Green ≥95%")
    )
    fig = px.bar(
        out.sort_values("absorption_pct"),
        x="project",
        y="absorption_pct",
        color="band",
        color_discrete_map={"Red <70%": "#ff4b4b", "Yellow 70–95%": "#f0b429", "Green ≥95%": "#3dd68c"},
        labels={"absorption_pct": "Absorption %"},
    )
    fig.update_layout(xaxis_tickangle=-35)
    return _style(fig, "Absorption rate by project")


def sold_unsold_donut(sold: int, unsold: int) -> go.Figure:
    fig = go.Figure(
        data=[
            go.Pie(
                labels=["Sold", "Unsold"],
                values=[sold, unsold],
                hole=0.58,
                marker_colors=["#3dd68c", "#ff4b4b"],
                textinfo="label+percent",
            )
        ]
    )
    return _style(fig, "Sold vs unsold split")


def price_absorption_bubble(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return _empty("No projects")
    fig = px.scatter(
        df,
        x="price_psf",
        y="absorption_pct",
        size="total_units",
        color="developer",
        hover_name="project",
        labels={"price_psf": "Price ₹/sqft", "absorption_pct": "Absorption %"},
        color_discrete_sequence=PALETTE,
    )
    return _style(fig, "Price vs absorption (bubble = units)")


def stacked_sold_unsold(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return _empty("No projects")
    melt = df.melt(id_vars=["project"], value_vars=["units_sold", "units_unsold"], var_name="status", value_name="units")
    fig = px.bar(
        melt,
        x="project",
        y="units",
        color="status",
        barmode="stack",
        color_discrete_map={"units_sold": "#3dd68c", "units_unsold": "#ff4b4b"},
    )
    return _style(fig, "Sold vs unsold by project")


def ml_vs_actual_chart(pred: pd.DataFrame) -> go.Figure:
    if pred.empty:
        return _empty("No forecast rows")
    fig = px.bar(
        pred,
        x="project",
        y=["absorption_pct", "ml_forecast_pct"],
        barmode="group",
        color_discrete_sequence=PALETTE[:2],
    )
    fig.update_layout(xaxis_tickangle=-30)
    return _style(fig, "Actual vs ML absorption forecast")


def twin_curves(months, baseline, intervention, cannibalized=None) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=months, y=baseline, name="Baseline (no rival)", mode="lines+markers", line=dict(color="#58a6ff", width=2.5)))
    if cannibalized is not None:
        fig.add_trace(go.Scatter(x=months, y=cannibalized, name="With rival cannibalization", mode="lines+markers", line=dict(color="#ff4b4b", width=2.2)))
    fig.add_trace(go.Scatter(x=months, y=intervention, name="Prescriptive intervention", mode="lines+markers", line=dict(color="#3dd68c", width=2.5)))
    fig.update_layout(xaxis_title="Month", yaxis_title="Cumulative units sold")
    return _style(fig, "Digital twin — competitive cannibalization")


def imr_i_chart(index, values, ucl, lcl, xbar) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=index, y=values, mode="lines+markers", name="I", line=dict(color="#58a6ff")))
    fig.add_hline(y=ucl, line_dash="dash", line_color="#ff4b4b", annotation_text="UCL")
    fig.add_hline(y=lcl, line_dash="dash", line_color="#ff4b4b", annotation_text="LCL")
    fig.add_hline(y=xbar, line_dash="dot", line_color="#8b949e", annotation_text="CL")
    return _style(fig, "I-Chart (Individual)")


def imr_mr_chart(mr_values, mr_ucl, mrbar) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Scatter(y=list(mr_values), mode="lines+markers", name="MR", line=dict(color="#3dd68c")))
    fig.add_hline(y=mr_ucl, line_dash="dash", line_color="#ff4b4b", annotation_text="MR UCL")
    fig.add_hline(y=mrbar, line_dash="dot", line_color="#8b949e", annotation_text="MR bar")
    return _style(fig, "Moving Range chart")
