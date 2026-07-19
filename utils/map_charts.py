"""Map DSS chart helpers — dark theme."""
from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from utils.charts import PALETTE, _style

BLUE = "#58a6ff"
GREEN = "#3dd68c"


def radar_chart(values: dict[str, float], title: str = "Suitability radar") -> go.Figure:
    cats = list(values.keys())
    vals = list(values.values())
    fig = go.Figure(
        data=[
            go.Scatterpolar(
                r=vals + [vals[0]],
                theta=cats + [cats[0]],
                fill="toself",
                name=title,
                line_color=GREEN,
                fillcolor="rgba(61,214,140,0.25)",
            )
        ]
    )
    fig.update_layout(
        polar=dict(
            bgcolor="#161b22",
            radialaxis=dict(visible=True, range=[0, 100], gridcolor="#30363d", color="#8b949e"),
            angularaxis=dict(gridcolor="#30363d", color="#c9d1d9"),
        )
    )
    return _style(fig, title)


def dual_radar(a: dict[str, float], b: dict[str, float], name_a: str, name_b: str) -> go.Figure:
    cats = list(a.keys())
    fig = go.Figure()
    fig.add_trace(
        go.Scatterpolar(
            r=list(a.values()) + [list(a.values())[0]],
            theta=cats + [cats[0]],
            fill="toself",
            name=name_a,
            line_color=BLUE,
            fillcolor="rgba(88,166,255,0.2)",
        )
    )
    fig.add_trace(
        go.Scatterpolar(
            r=list(b.values()) + [list(b.values())[0]],
            theta=cats + [cats[0]],
            fill="toself",
            name=name_b,
            line_color=GREEN,
            fillcolor="rgba(61,214,140,0.18)",
        )
    )
    fig.update_layout(
        polar=dict(
            bgcolor="#161b22",
            radialaxis=dict(visible=True, range=[0, 100], gridcolor="#30363d", color="#8b949e"),
            angularaxis=dict(gridcolor="#30363d", color="#c9d1d9"),
        )
    )
    return _style(fig, "Area comparison radar")


def price_bar(df: pd.DataFrame) -> go.Figure:
    fig = px.bar(
        df.sort_values("avg_price_psf"),
        x="avg_price_psf",
        y="zone",
        orientation="h",
        color="suitability_score",
        color_continuous_scale=["#ff4b4b", "#f0b429", "#3dd68c"],
    )
    return _style(fig, "Price Rs/sqft by area")


def correlation_heatmap(df: pd.DataFrame) -> go.Figure:
    num = df.select_dtypes(include="number")
    corr = num.corr()
    fig = px.imshow(corr, text_auto=".2f", color_continuous_scale="Tealgrn", aspect="auto")
    return _style(fig, "Feature correlation heatmap")


def heatmap_scatter(df: pd.DataFrame) -> go.Figure:
    fig = px.scatter_mapbox(
        df,
        lat="lat",
        lon="lon",
        size="population_growth_index",
        color="suitability_score",
        hover_name="zone",
        hover_data={
            "avg_price_psf": True,
            "price_trend_yoy_pct": True,
            "suitability_label": True,
            "lat": False,
            "lon": False,
        },
        color_continuous_scale=["#ff4b4b", "#f0b429", "#3dd68c"],
        size_max=28,
        zoom=9.5,
        height=520,
    )
    fig.update_layout(
        mapbox_style="carto-darkmatter",
        margin=dict(t=40, b=0, l=0, r=0),
        paper_bgcolor="#1c2128",
        font=dict(color="#c9d1d9"),
    )
    return fig


def importance_chart(imp: pd.DataFrame) -> go.Figure:
    fig = px.bar(imp, x="importance", y="feature", orientation="h", color_discrete_sequence=[BLUE])
    return _style(fig, "RF feature importance (suitability drivers)")
