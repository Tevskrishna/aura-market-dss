"""
Dynamic visualization studio — click chips / generate buttons to rebuild charts.

Benchmarks: Zillow/Redfin live filter refresh + proptech map-first decision surfaces.
"""
from __future__ import annotations

from collections.abc import Callable
from typing import Any

import streamlit as st


def graphic_html(relative_path: str, css_class: str = "dss-graphic") -> None:
    """Inline an SVG/PNG from assets/graphics via markdown image or raw SVG."""
    from config import settings

    path = settings.ASSETS_DIR / "graphics" / relative_path
    if not path.exists():
        return
    if path.suffix.lower() == ".svg":
        st.html(f'<div class="{css_class}">{path.read_text(encoding="utf-8")}</div>')
    else:
        st.image(str(path), use_container_width=True)


def scenario_bar(
    key: str,
    label: str,
    options: list[str],
    default: str | None = None,
) -> str:
    """Segmented scenario control — changing it rebuilds charts on next generate/rerun."""
    default = default or options[0]
    st.caption(label)
    choice = st.segmented_control(
        label,
        options=options,
        default=default,
        key=key,
        label_visibility="collapsed",
        width="stretch",
    )
    return choice or default


def generate_button(key: str, text: str = "Generate live graphics") -> bool:
    """Primary CTA — bumps a nonce so charts regenerate with motion seed."""
    c1, c2 = st.columns([1.4, 2])
    with c1:
        clicked = st.button(text, key=f"{key}_gen", type="primary", width="stretch")
    with c2:
        st.caption("Click to regenerate charts for the selected scenario · works on phone & desktop")
    if clicked:
        st.session_state[f"{key}_nonce"] = int(st.session_state.get(f"{key}_nonce", 0)) + 1
    return clicked


def viz_nonce(key: str) -> int:
    return int(st.session_state.get(f"{key}_nonce", 0))


def action_pills(key: str, options: list[str], default: str | None = None) -> str:
    default = default or options[0]
    picked = st.pills(
        "Focus",
        options=options,
        default=default,
        key=f"{key}_pills",
        label_visibility="collapsed",
    )
    return picked or default


def live_kpi_strip(cards: list[dict[str, Any]]) -> None:
    """Animated KPI HTML strip — feels dynamic vs static st.metric."""
    bits = []
    for card in cards:
        bits.append(
            f'<div class="dss-live-kpi">'
            f'<div class="dss-live-kpi-label">{card.get("label","")}</div>'
            f'<div class="dss-live-kpi-value" data-count="{card.get("value","")}">{card.get("display", card.get("value",""))}</div>'
            f'<div class="dss-live-kpi-hint">{card.get("hint","")}</div>'
            f"</div>"
        )
    st.html(f'<div class="dss-live-kpi-grid">{"".join(bits)}</div>')


def cockpit_hero(
    title: str,
    subtitle: str,
    bullets: list[str],
) -> None:
    items = "".join(f"<li>{b}</li>" for b in bullets)
    from config import settings

    svg = (settings.ASSETS_DIR / "graphics" / "hero-skyline.svg").read_text(encoding="utf-8")
    st.html(
        f'<div class="dss-cockpit">'
        f'<div class="dss-cockpit-visual">{svg}</div>'
        f'<div class="dss-cockpit-copy">'
        f'<div class="dss-kicker">PROPTECH DECISION COCKPIT</div>'
        f"<h1>{title}</h1>"
        f"<p>{subtitle}</p>"
        f'<ul class="dss-cockpit-list">{items}</ul>'
        f"</div></div>"
    )


def render_dynamic_figure(
    key: str,
    builder: Callable[[], Any],
    *,
    height: int | None = None,
) -> None:
    """Rebuild Plotly figure whenever nonce changes; inject animation-ish transition."""
    _ = viz_nonce(key)  # dependency for Streamlit rerun semantics
    fig = builder()
    if height and hasattr(fig, "update_layout"):
        fig.update_layout(height=height)
    if hasattr(fig, "update_layout"):
        fig.update_layout(transition_duration=400)
    st.plotly_chart(fig, width="stretch", key=f"{key}_chart_{viz_nonce(key)}")
