"""
Dynamic visualization studio — lenses and generate actually remount charts.

Streamlit keeps Plotly widgets glued to a stable `key`. If only the lens
changes and the key stays the same, the old figure can appear "stuck".
We bake scene + nonce into the chart key so options visibly switch.
"""
from __future__ import annotations

import re
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


def _slug(text: str) -> str:
    return re.sub(r"[^a-zA-Z0-9]+", "_", str(text)).strip("_")[:48] or "default"


def scenario_bar(
    key: str,
    label: str,
    options: list[str],
    default: str | None = None,
) -> str:
    """Layer / lens control that must remount charts when the selection changes.

    Prefer radio over segmented_control: Streamlit often ignores clicks when both
    ``default=`` and ``key=`` are passed to segmented_control / pills.
    """
    fallback = default if default in options else options[0]
    if key not in st.session_state or st.session_state.get(key) not in options:
        st.session_state[key] = fallback

    st.caption(label)
    # Horizontal radio is the most reliable "tab" widget across Streamlit versions.
    choice = st.radio(
        label,
        options=options,
        key=key,
        horizontal=True,
        label_visibility="collapsed",
    )
    picked = choice if choice in options else fallback
    st.session_state[f"{key}_scene"] = picked
    return picked


def generate_button(key: str, text: str = "Generate live graphics") -> bool:
    """Bump nonce so Plotly remounts; show toast so the click never feels dead."""
    c1, c2 = st.columns([1.4, 2])
    with c1:
        clicked = st.button(text, key=f"{key}_gen", type="primary", width="stretch")
    with c2:
        st.caption("Lens = switch graphic · Generate = force remount / refresh")
    if clicked:
        st.session_state[f"{key}_nonce"] = int(st.session_state.get(f"{key}_nonce", 0)) + 1
        st.session_state[f"{key}_flash"] = True
        try:
            st.toast("Graphics refreshed", icon="✅")
        except Exception:
            pass
    return clicked


def viz_nonce(key: str) -> int:
    return int(st.session_state.get(f"{key}_nonce", 0))


def action_pills(key: str, options: list[str], default: str | None = None) -> str:
    pill_key = f"{key}_pills"
    fallback = default if default in options else options[0]
    if pill_key not in st.session_state or st.session_state.get(pill_key) not in options:
        st.session_state[pill_key] = fallback
    picked = st.radio(
        "Focus",
        options=options,
        key=pill_key,
        horizontal=True,
        label_visibility="collapsed",
    )
    return picked if picked in options else fallback


def live_kpi_strip(cards: list[dict[str, Any]]) -> None:
    """Animated KPI HTML strip — display only (not clickable)."""
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


def linked_kpi_lens_strip(
    cards: list[dict[str, Any]],
    *,
    lens_key: str,
    pending_key: str = "_pending_lens",
) -> None:
    """Scorecard figures as buttons — tap a KPI to switch the graphics layer."""
    cols = st.columns(len(cards))
    for i, (col, card) in enumerate(zip(cols, cards)):
        lens = str(card.get("lens") or "")
        active = st.session_state.get(lens_key) == lens
        label = f"{card.get('label', '')}\n{card.get('display', card.get('value', ''))}"
        # Keys must be unique even when two KPIs share the same lens (e.g. UC + UC unsold).
        btn_key = f"{lens_key}_kpi_{i}_{_slug(str(card.get('label', '')))}_{_slug(lens)}"
        with col:
            if st.button(
                label,
                key=btn_key,
                type="primary" if active else "secondary",
                width="stretch",
                help=str(card.get("hint") or f"Show {lens}"),
                disabled=not lens,
            ):
                st.session_state[pending_key] = lens
                st.rerun()


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
    scene: str | None = None,
) -> None:
    """
    Rebuild Plotly whenever nonce OR scene changes.
    `scene` must be the lens / tab selection string so switches remount.
    """
    nonce = viz_nonce(key)
    scene_val = scene if scene is not None else str(st.session_state.get(f"{key}_scene", ""))
    fig = builder()
    if height and hasattr(fig, "update_layout"):
        fig.update_layout(height=height)
    if hasattr(fig, "update_layout"):
        # Visible title stamp so user sees regenerates even when shape is similar
        stamp = f" · live #{nonce}" if nonce else ""
        title = fig.layout.title.text if fig.layout.title and fig.layout.title.text else ""
        if stamp and title and "live #" not in str(title):
            fig.update_layout(title=f"{title}{stamp}")
        elif stamp and not title and scene_val:
            fig.update_layout(title=f"{scene_val}{stamp}")
        fig.update_layout(transition_duration=350)
    if st.session_state.pop(f"{key}_flash", None):
        st.success(f"Refreshed · {scene_val or 'current view'} · pass #{nonce}")
    chart_key = f"{key}_chart_{nonce}_{_slug(scene_val)}"
    st.plotly_chart(fig, width="stretch", key=chart_key)
