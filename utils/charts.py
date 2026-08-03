"""
Plotly chart builders — Stitch institutional light palette.
"""
from __future__ import annotations

import re

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from config import settings

BG = "#ffffff"
PAPER = "#ffffff"
TEXT = "#1b1c1c"
MUTED = "#5f5e5b"
GRID = "#efeded"
ACCENT = "#b97343"
BLUE = "#1b1c1c"
GREEN = "#1b3022"
PALETTE = ["#b97343", "#1b3022", "#1b1c1c", "#8a5a2b", "#5f5e5b", "#747878", "#c4c7c7"]


def _quarter_sort_key(period) -> tuple[int, int]:
    """Sort Q1-2023 / 2023-Q1 chronologically (not alphabetically)."""
    s = str(period).strip()
    m = re.match(r"Q(\d)\s*[-/]\s*(\d{4})", s, re.I)
    if m:
        return (int(m.group(2)), int(m.group(1)))
    m = re.match(r"(\d{4})\s*[-/]\s*Q(\d)", s, re.I)
    if m:
        return (int(m.group(1)), int(m.group(2)))
    ts = pd.to_datetime(s, errors="coerce")
    if pd.notna(ts):
        return (int(ts.year), int(ts.quarter))
    return (9999, 0)


def _style(fig: go.Figure, title: str | None = None) -> go.Figure:
    """Title above, legend below — avoids Plotly modebar / legend collisions."""
    title_text = str(title).strip() if title else ""
    # Remove empty titles entirely — Streamlit/Plotly can paint the literal "undefined"
    if title_text:
        fig.update_layout(
            title=dict(
                text=title_text,
                font=dict(family="Playfair Display, Georgia, serif", size=16, color=TEXT),
                x=0,
                xanchor="left",
                y=0.98,
                yanchor="top",
                pad=dict(t=0, b=8),
            ),
            margin=dict(t=56, b=120, l=48, r=28),
        )
    else:
        fig.update_layout(title=None, margin=dict(t=28, b=120, l=48, r=28))
        try:
            fig.layout.pop("title", None)
        except Exception:
            pass

    fig.update_layout(
        height=max(settings.CHART_HEIGHT, 420),
        paper_bgcolor=PAPER,
        plot_bgcolor=BG,
        font=dict(family="Geist, Segoe UI, sans-serif", color=TEXT, size=12),
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.18,
            x=0,
            xanchor="left",
            bgcolor="rgba(0,0,0,0)",
            font=dict(color=TEXT, size=11),
        ),
        colorway=PALETTE,
        hoverlabel=dict(bgcolor="#1c1b1b", font_size=12, font_family="Geist", font_color="#fbf9f8"),
        transition=dict(duration=550, easing="cubic-in-out"),
    )
    fig.update_xaxes(showgrid=False, linecolor=GRID, tickfont=dict(color=MUTED), gridcolor=GRID, zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor=GRID, linecolor=GRID, tickfont=dict(color=MUTED), zeroline=False)
    return apply_entrance_motion(fig)


def apply_entrance_motion(
    fig: go.Figure,
    *,
    max_frames: int = 24,
    start_empty: bool = False,
) -> go.Figure:
    """
    Add Play / draw-in animation frames for line & bar charts.
    start_empty=True begins at frame 0 so the draw-in is visible.
    """
    if fig is None or not getattr(fig, "data", None):
        return fig
    if getattr(fig, "frames", None):
        return fig  # already animated (e.g. scenario scrubber)
    try:
        traces = list(fig.data)
        kinds = {getattr(t, "type", "") for t in traces}
        if not kinds.intersection({"scatter", "bar", "scattergl"}):
            return fig

        # Line / scatter: reveal points left → right
        if "scatter" in kinds or "scattergl" in kinds:
            lengths = []
            for t in traces:
                if getattr(t, "type", "") not in ("scatter", "scattergl"):
                    continue
                xs = list(t.x) if t.x is not None else []
                lengths.append(len(xs))
            n = max(lengths) if lengths else 0
            if n < 3:
                return fig
            step = max(1, n // max_frames)
            idxs = list(range(step, n, step))
            if idxs[-1] != n:
                idxs.append(n)
            frames = []
            for k in idxs:
                frame_data = []
                for t in traces:
                    if getattr(t, "type", "") not in ("scatter", "scattergl"):
                        frame_data.append(t)
                        continue
                    xs = list(t.x) if t.x is not None else []
                    ys = list(t.y) if t.y is not None else []
                    frame_data.append(
                        go.Scatter(
                            x=xs[:k],
                            y=ys[:k],
                            mode=t.mode,
                            name=t.name,
                            line=t.line,
                            marker=t.marker,
                            fill=t.fill,
                            fillcolor=t.fillcolor,
                            showlegend=t.showlegend,
                        )
                    )
                frames.append(go.Frame(data=frame_data, name=str(k)))
            fig.frames = frames
            if start_empty and frames:
                first = frames[0].data
                for i, tr in enumerate(first):
                    if i < len(fig.data) and getattr(fig.data[i], "type", "") in ("scatter", "scattergl"):
                        fig.data[i].x = tr.x
                        fig.data[i].y = tr.y

        elif "bar" in kinds:
            # Bars grow from zero (Play) — keep final values on screen initially
            n = max((len(list(t.y or t.x or [])) for t in traces), default=0)
            if n < 2:
                return fig
            frames = []
            steps = [0.15, 0.35, 0.55, 0.75, 1.0]
            full_ys = []
            for t in traces:
                ys = [float(v) if v is not None else 0.0 for v in (list(t.y) if t.y is not None else [])]
                full_ys.append(ys)
            for s in steps:
                frame_data = []
                for i, t in enumerate(traces):
                    ys = [v * s for v in full_ys[i]]
                    frame_data.append(go.Bar(x=t.x, y=ys, name=t.name, marker=t.marker, orientation=t.orientation))
                frames.append(go.Frame(data=frame_data, name=str(s)))
            fig.frames = frames
            if start_empty:
                for i, t in enumerate(fig.data):
                    if getattr(t, "type", "") == "bar":
                        t.y = [v * 0.05 for v in full_ys[i]]

        if not fig.frames:
            return fig

        # Terracotta Play control under the legend (inside plot so Streamlit does not clip it)
        fig.update_layout(
            updatemenus=[
                dict(
                    type="buttons",
                    direction="left",
                    x=0,
                    xanchor="left",
                    y=-0.34,
                    yanchor="top",
                    pad=dict(r=8, t=4),
                    showactive=False,
                    bgcolor="#b97343",
                    bordercolor="#b97343",
                    borderwidth=1,
                    font=dict(size=12, color="#ffffff", family="Geist"),
                    buttons=[
                        dict(
                            label="▶ Play animation",
                            method="animate",
                            args=[
                                None,
                                {
                                    "frame": {"duration": 100, "redraw": True},
                                    "fromcurrent": False,
                                    "transition": {"duration": 80, "easing": "cubic-in-out"},
                                },
                            ],
                        ),
                    ],
                )
            ],
            margin=dict(
                t=max(int(fig.layout.margin.t or 28), 28),
                b=max(int(fig.layout.margin.b or 96), 140),
            ),
        )
    except Exception:
        return fig
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


def inventory_trend_chart(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return _empty("No PropStack inventory trend")
    frame = df.copy()
    frame["month"] = pd.to_datetime(frame["month"].astype(str) + "-01", errors="coerce")
    fig = go.Figure()
    fig.add_trace(
        go.Bar(x=frame["month"], y=frame["absorbed_units"], name="Absorbed", marker_color=GREEN, opacity=0.9)
    )
    fig.add_trace(
        go.Scatter(
            x=frame["month"],
            y=frame["unsold_units"],
            name="Unsold",
            mode="lines+markers",
            line=dict(color=ACCENT, width=2.5),
            marker=dict(size=5),
            yaxis="y2",
        )
    )
    if "inventory_overhang_months" in frame.columns:
        fig.add_trace(
            go.Scatter(
                x=frame["month"],
                y=frame["inventory_overhang_months"],
                name="Overhang (mo)",
                mode="lines",
                line=dict(color=BLUE, width=2, dash="dot"),
                yaxis="y3",
                visible="legendonly",
            )
        )
    fig.update_layout(
        yaxis=dict(title="Absorbed units", gridcolor=GRID, color=MUTED),
        yaxis2=dict(title="Unsold", overlaying="y", side="right", showgrid=False, color=MUTED),
        yaxis3=dict(title="Overhang mo", overlaying="y", side="right", showgrid=False, visible=False),
    )
    return _style(fig, "PropStack inventory trend — absorbed vs unsold")


def weighted_price_trend_chart(df: pd.DataFrame) -> go.Figure:
    """Stitch Market chart — terracotta primary market + charcoal secondary."""
    if df.empty:
        return _empty("No PropStack price trend")
    frame = df.copy()
    if "period" in frame.columns:
        frame = frame.sort_values("period", key=lambda s: s.map(_quarter_sort_key))
    x = frame["period"] if "period" in frame.columns else frame.index
    primary = frame["wt_avg_absorbed_psf"]
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=x,
            y=primary,
            name="Primary market",
            mode="lines+markers",
            line=dict(color=ACCENT, width=2.8),
            marker=dict(size=7, color=ACCENT),
            fill="tozeroy",
            fillcolor="rgba(185,115,67,0.08)",
        )
    )
    if "wt_avg_available_psf" in frame.columns:
        fig.add_trace(
            go.Scatter(
                x=x,
                y=frame["wt_avg_available_psf"],
                name="Secondary / available",
                mode="lines+markers",
                line=dict(color=BLUE, width=2, dash="dash"),
                marker=dict(size=5, color=BLUE),
            )
        )
    elif "wt_avg_new_launch_psf" in frame.columns:
        fig.add_trace(
            go.Scatter(
                x=x,
                y=frame["wt_avg_new_launch_psf"],
                name="New launch",
                mode="lines+markers",
                line=dict(color=BLUE, width=2, dash="dash"),
                marker=dict(size=5, color=BLUE),
            )
        )
    # Annotate peak on primary series
    try:
        vals = primary.astype(float)
        i = int(vals.to_numpy().argmax())
        px_ = x.iloc[i] if hasattr(x, "iloc") else list(x)[i]
        py_ = float(vals.iloc[i])
        fig.add_annotation(
            x=px_,
            y=py_,
            text=f"Peak · ₹{py_:,.0f}",
            showarrow=True,
            arrowhead=2,
            ax=40,
            ay=-35,
            font=dict(size=11, color=ACCENT, family="Geist"),
            bgcolor="rgba(255,255,255,0.9)",
            bordercolor=ACCENT,
            borderwidth=1,
        )
    except Exception:
        pass
    if "period" in frame.columns:
        periods = list(dict.fromkeys(frame["period"].tolist()))
        fig.update_xaxes(categoryorder="array", categoryarray=periods)
    fig.update_yaxes(title_text="₹ / sqft", showgrid=True, gridcolor=GRID)
    return _style(fig, None)  # page card owns the title — no Plotly title


def new_launch_pulse_chart(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return _empty("No PropStack new-launch pulse")
    frame = df.copy()
    frame["month"] = pd.to_datetime(frame["month"].astype(str) + "-01", errors="coerce")
    frame = frame.sort_values("month")
    fig = go.Figure()
    fig.add_trace(go.Bar(x=frame["month"], y=frame["units_launched"], name="Units launched", marker_color=BLUE))
    if "absorbed_units" in frame.columns:
        fig.add_trace(
            go.Scatter(
                x=frame["month"],
                y=frame["absorbed_units"],
                name="Absorbed at launch month",
                mode="lines+markers",
                line=dict(color=GREEN, width=2.5),
                yaxis="y2",
            )
        )
        fig.update_layout(
            yaxis=dict(title="Units launched", gridcolor=GRID, color=MUTED),
            yaxis2=dict(title="Absorbed", overlaying="y", side="right", showgrid=False, color=MUTED),
        )
    return _style(fig, "New launch pulse")


def absorption_price_band_chart(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return _empty("No PropStack absorption by price band")
    frame = df.copy()
    order = [
        "<4000",
        "4001-5000",
        "5001-6000",
        "6001-7000",
        "7001-8000",
        "8001-9000",
        "9001-10000",
        "10001-11000",
        "11001-12000",
        ">12000",
    ]
    frame["price_band"] = pd.Categorical(frame["price_band"].astype(str), categories=order, ordered=True)
    frame["_qsort"] = frame["period"].map(_quarter_sort_key)
    frame = frame.sort_values(["_qsort", "price_band"])
    periods = sorted(frame["period"].dropna().unique(), key=_quarter_sort_key)
    fig = px.bar(
        frame,
        x="period",
        y="units",
        color="price_band",
        category_orders={"period": periods, "price_band": order},
        labels={"units": "Absorbed units", "period": "Quarter", "price_band": "₹/sqft band"},
        color_discrete_sequence=PALETTE,
    )
    fig.update_xaxes(categoryorder="array", categoryarray=periods, tickangle=-30)
    return _style(fig, "Absorption by price band")


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
