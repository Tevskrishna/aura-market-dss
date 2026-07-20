"""
Visual Experience Mode — optional presentation layer only.

Default OFF = calm enterprise UI.
When ON: lightweight 3D / depth / animation that aid comprehension of
location, comparison, relationships, or scenarios.

Never changes scoring, AI/ML, engines, adapters, or navigation.
"""
from __future__ import annotations

from typing import Any, Literal

import streamlit as st

VISUAL_KEY = "iq_visual_experience"

Purpose = Literal["comparison", "scenario", "location", "relationship", "generic"]


def visual_experience_on() -> bool:
    """True only when the user enables Visual Experience in Settings."""
    return bool(st.session_state.get(VISUAL_KEY, False))


def render_visual_experience_toggle() -> bool:
    """Sidebar Settings control — default off."""
    st.sidebar.toggle(
        "Visual Experience Mode",
        value=bool(st.session_state.get(VISUAL_KEY, False)),
        key=VISUAL_KEY,
        help=(
            "Optional. Adds light 3D / motion / depth only where it clarifies "
            "location, comparison, relationships, or scenarios. "
            "Off = calm enterprise UI. Does not change decisions or math."
        ),
    )
    on = visual_experience_on()
    if on:
        st.sidebar.caption("Visual Experience on · presentation only")
    return on


def inject_visual_experience_chrome() -> None:
    """Load CSS + honesty strip when mode is on. No-op when off."""
    if not visual_experience_on():
        return
    from config import settings

    path = settings.ASSETS_DIR / "visual_experience.css"
    if path.exists():
        st.html(f"<style>{path.read_text(encoding='utf-8')}</style>")
    st.html(
        '<div class="iq-vx-banner" role="status">'
        "<strong>Visual Experience Mode</strong>"
        "<span>Presentation only — same Hub GO/HOLD math · same data contract</span>"
        "</div>"
    )


def enhance_figure(fig: Any, *, purpose: Purpose = "generic") -> Any:
    """
    Mutate Plotly figure presentation when Visual Experience is on.
    Returns the same figure object; safe no-op when mode is off or fig is empty.
    """
    if fig is None or not visual_experience_on():
        return fig
    if not hasattr(fig, "update_layout"):
        return fig

    # Shared: slower, clearer transitions when lenses/scenarios change
    fig.update_layout(transition={"duration": 650, "easing": "cubic-in-out"})

    if purpose == "scenario":
        _enhance_scenario_relationships(fig)
    elif purpose == "comparison":
        _enhance_comparison(fig)
    elif purpose == "location":
        _enhance_location(fig)
    elif purpose == "relationship":
        _enhance_relationship(fig)

    return fig


def _enhance_scenario_relationships(fig: Any) -> None:
    """Fill gaps between scenario paths so blind-spot / recovery is visible as area."""
    try:
        traces = list(fig.data)
        if len(traces) < 2:
            return
        # Soften markers; emphasize path differences
        for t in traces:
            if hasattr(t, "mode") and t.mode and "lines" in str(t.mode):
                t.update(line=dict(width=3))
        # Shade under intervention vs baseline when both present
        names = [str(getattr(t, "name", "") or "") for t in traces]
        base_i = next((i for i, n in enumerate(names) if "baseline" in n.lower()), None)
        rival_i = next((i for i, n in enumerate(names) if "rival" in n.lower() or "cannibal" in n.lower()), None)
        if base_i is not None and rival_i is not None:
            traces[rival_i].update(fill="tonexty", fillcolor="rgba(255, 75, 75, 0.18)")
        fig.update_layout(
            legend=dict(orientation="h", yanchor="bottom", y=1.02),
            annotations=[
                dict(
                    text="Shaded gap = rival impact path (directional)",
                    xref="paper",
                    yref="paper",
                    x=0,
                    y=-0.14,
                    showarrow=False,
                    font=dict(size=11, color="#8a9bb0"),
                )
            ],
            margin=dict(b=72),
        )
    except Exception:
        pass


def _enhance_comparison(fig: Any) -> None:
    """Stronger bar contrast for year / category comparisons."""
    try:
        fig.update_traces(
            marker=dict(line=dict(width=0.5, color="rgba(255,255,255,0.25)")),
            selector=dict(type="bar"),
        )
        fig.update_layout(bargap=0.22, bargroupgap=0.08)
    except Exception:
        pass


def _enhance_location(fig: Any) -> None:
    """Depth cue on geo/spatial scatters — larger hover labels."""
    try:
        fig.update_traces(
            marker=dict(line=dict(width=1, color="rgba(255,255,255,0.35)")),
            selector=dict(type="scatter"),
        )
        fig.update_layout(hovermode="closest")
    except Exception:
        pass


def _enhance_relationship(fig: Any) -> None:
    """Emphasize multi-axis relationships (size/color already encode factors)."""
    try:
        fig.update_layout(hovermode="closest")
        fig.update_traces(selector=dict(type="scatter"), marker=dict(opacity=0.9))
    except Exception:
        pass


def try_comparison_3d_bars(
    labels: list[str],
    values: list[float],
    *,
    title: str,
    x_title: str = "",
    y_title: str = "Value",
) -> Any | None:
    """
    Lightweight 3D bars for category comparison (e.g. RERA by year).
    Returns None when Visual Experience is off — caller keeps 2D chart.
    """
    if not visual_experience_on() or not labels or not values:
        return None
    try:
        import plotly.graph_objects as go

        from utils.charts import _style

        xs, ys, zs = [], [], []
        for i, (lab, val) in enumerate(zip(labels, values)):
            # Each bar as a thin 3D column along x
            xs.extend([i, i, i, i, i, None])
            ys.extend([0, 1, 1, 0, 0, None])
            zs.extend([0, 0, float(val), float(val), 0, None])
        fig = go.Figure(
            data=[
                go.Scatter3d(
                    x=xs,
                    y=ys,
                    z=zs,
                    mode="lines",
                    line=dict(color="#58a6ff", width=8),
                    name="Level",
                    hoverinfo="skip",
                ),
                go.Scatter3d(
                    x=list(range(len(labels))),
                    y=[0.5] * len(labels),
                    z=[float(v) for v in values],
                    mode="markers+text",
                    marker=dict(size=6, color="#3de0d0"),
                    text=[str(int(v)) if float(v) == int(v) else f"{v:.1f}" for v in values],
                    textposition="top center",
                    name=y_title,
                    hovertext=[f"{a}: {b}" for a, b in zip(labels, values)],
                    hoverinfo="text",
                ),
            ]
        )
        fig.update_layout(
            scene=dict(
                xaxis=dict(
                    title=x_title or "Category",
                    tickvals=list(range(len(labels))),
                    ticktext=[str(l) for l in labels],
                ),
                yaxis=dict(title="", showticklabels=False, range=[-0.2, 1.2]),
                zaxis=dict(title=y_title),
                camera=dict(eye=dict(x=1.5, y=1.6, z=0.9)),
            ),
            height=420,
            margin=dict(l=0, r=0, t=48, b=0),
        )
        return _style(fig, title + " · 3D compare")
    except Exception:
        return None


def try_location_3d_scatter(
    df: Any,
    *,
    x: str,
    y: str,
    z: str,
    color: str | None = None,
    hover_name: str | None = None,
    title: str = "Location relationship",
) -> Any | None:
    """3D scatter for zone relationships (price × risk × score). Off → None."""
    if not visual_experience_on() or df is None or getattr(df, "empty", True):
        return None
    try:
        import plotly.express as px

        from utils.charts import _style

        kwargs = dict(data_frame=df, x=x, y=y, z=z, title=title)
        if color and color in df.columns:
            kwargs["color"] = color
        if hover_name and hover_name in df.columns:
            kwargs["hover_name"] = hover_name
        fig = px.scatter_3d(**kwargs)
        fig.update_traces(marker=dict(size=7))
        fig.update_layout(
            scene_camera=dict(eye=dict(x=1.6, y=1.4, z=1.1)),
            height=440,
            margin=dict(l=0, r=0, t=48, b=0),
        )
        return _style(fig, title + " · 3D relationship")
    except Exception:
        return None


def try_scenario_month_frames(
    months: list | Any,
    baseline: list | Any,
    intervention: list | Any,
    cannibalized: list | Any | None,
    *,
    title: str = "Scenario paths over time",
) -> Any | None:
    """
    Animated month scrubber — how paths diverge over the horizon.
    Aids scenario comprehension; off → None (static twin_curves used).
    """
    if not visual_experience_on():
        return None
    try:
        import pandas as pd
        import plotly.express as px

        from utils.charts import _style

        rows = []
        for i, m in enumerate(months):
            rows.append({"month": m, "frame": int(m), "path": "Baseline", "units": float(baseline[i])})
            rows.append({"month": m, "frame": int(m), "path": "Intervene", "units": float(intervention[i])})
            if cannibalized is not None:
                rows.append(
                    {
                        "month": m,
                        "frame": int(m),
                        "path": "Rival pressure",
                        "units": float(cannibalized[i]),
                    }
                )
        long = pd.DataFrame(rows)
        # Cumulative reveal: each frame shows history up to that month
        frames_df = []
        for fr in sorted(long["frame"].unique()):
            chunk = long[long["frame"] <= fr].copy()
            chunk["frame_id"] = fr
            frames_df.append(chunk)
        anim = pd.concat(frames_df, ignore_index=True)
        fig = px.line(
            anim,
            x="month",
            y="units",
            color="path",
            animation_frame="frame_id",
            markers=True,
            color_discrete_map={
                "Baseline": "#58a6ff",
                "Intervene": "#3dd68c",
                "Rival pressure": "#ff4b4b",
            },
        )
        fig.update_layout(
            xaxis_title="Month",
            yaxis_title="Cumulative units sold",
            height=440,
        )
        return _style(fig, title + " · scrub months")
    except Exception:
        return None
