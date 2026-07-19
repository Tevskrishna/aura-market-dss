"""
Plotly chart builders — dark enterprise palette matching accepted Map DSS UI.
"""
from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from config import settings

BG = "#1c2128"
PAPER = "#1c2128"
TEXT = "#c9d1d9"
MUTED = "#8b949e"
GRID = "#30363d"
ACCENT = "#ff4b4b"
BLUE = "#58a6ff"
GREEN = "#3dd68c"
PALETTE = ["#58a6ff", "#3dd68c", "#ff4b4b", "#f0b429", "#39d0d8", "#a371f7", "#ff7b72"]


def _style(fig: go.Figure, title: str | None = None) -> go.Figure:
    fig.update_layout(
        title=dict(text=title, font=dict(family="Inter, sans-serif", size=14, color="#e6edf3")) if title else None,
        height=settings.CHART_HEIGHT,
        margin=dict(t=55, b=36, l=40, r=20),
        paper_bgcolor=PAPER,
        plot_bgcolor=BG,
        font=dict(family="Inter, Segoe UI, sans-serif", color=TEXT, size=12),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0, bgcolor="rgba(0,0,0,0)", font=dict(color=TEXT)),
        colorway=PALETTE,
        hoverlabel=dict(bgcolor="#161b22", font_size=12, font_family="Inter", font_color="#e6edf3"),
    )
    fig.update_xaxes(showgrid=False, linecolor=GRID, tickfont=dict(color=MUTED), gridcolor=GRID, zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor=GRID, linecolor=GRID, tickfont=dict(color=MUTED), zeroline=False)
    return fig


def booking_trend_chart(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return _empty("No booking data for current filters")
    fig = px.area(df, x="month", y="bookings", labels={"month": "Month", "bookings": "Confirmed bookings"})
    fig.update_traces(line_color=GREEN, fillcolor="rgba(61,214,140,0.18)")
    return _style(fig, "Booking trend")


def project_comparison_chart(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return _empty("No projects for current filters")
    fig = px.bar(
        df,
        x="absorption_pct",
        y="project",
        color="developer",
        orientation="h",
        labels={"absorption_pct": "Absorption %", "project": "Project"},
        color_discrete_sequence=PALETTE,
    )
    fig.update_layout(height=max(settings.CHART_HEIGHT, 28 * len(df) + 120))
    return _style(fig, "Project comparison — absorption %")


def quarterly_performance_chart(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return _empty("No quarterly data for current filters")
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df["fy_quarter"], y=df["units_sold"], name="Units sold", marker_color=BLUE, opacity=0.95))
    fig.add_trace(
        go.Scatter(
            x=df["fy_quarter"],
            y=df["bookings"],
            name="Bookings",
            mode="lines+markers",
            line=dict(color=GREEN, width=2.5),
            marker=dict(size=7),
            yaxis="y2",
        )
    )
    fig.update_layout(
        yaxis=dict(title="Units sold", gridcolor=GRID, color=MUTED),
        yaxis2=dict(title="Bookings", overlaying="y", side="right", showgrid=False, color=MUTED),
    )
    return _style(fig, "Quarterly performance")


def marketing_efficiency_chart(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return _empty("No marketing spend data for current filters")
    size_col = "bookings" if df["bookings"].sum() > 0 else "spend_cr"
    fig = px.scatter(
        df,
        x="spend_cr",
        y="efficiency",
        size=size_col,
        color="project",
        hover_data=["sales_value_cr", "bookings"],
        labels={"spend_cr": "SMC spend (₹ Cr)", "efficiency": "Efficiency"},
        color_discrete_sequence=PALETTE,
    )
    return _style(fig, "Marketing efficiency (outcome per ₹ Cr)")


def buyer_mix_chart(distribution: dict[str, int]) -> go.Figure:
    if not distribution:
        return _empty("No buyer mix for current filters")
    df = pd.DataFrame({"segment": list(distribution.keys()), "count": list(distribution.values())})
    fig = px.pie(df, names="segment", values="count", hole=0.55, color_discrete_sequence=PALETTE)
    fig.update_traces(textposition="outside", textinfo="percent+label", textfont_color=TEXT)
    return _style(fig, "Buyer distribution — unit mix")


def _empty(message: str) -> go.Figure:
    fig = go.Figure()
    fig.add_annotation(text=message, xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False, font=dict(color=MUTED))
    fig.update_layout(
        height=260,
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        paper_bgcolor=PAPER,
        plot_bgcolor=BG,
    )
    return fig
