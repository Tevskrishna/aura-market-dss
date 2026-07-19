"""
Touch-first module navigation — graphical tiles + sidebar buttons.
Streamlit's auto pages list is hidden; these controls are the only jump UX.
"""
from __future__ import annotations

import html
from pathlib import Path

import streamlit as st

from components.layout import MODULE_NAV, _current_nav_label


TOUCH_TILES: list[tuple[str, str, str, str]] = [
    ("🎯", "Executive Hub", "app.py", "GO / HOLD / NO-GO threat score"),
    ("📈", "Market Intelligence", "pages/1_Market_Overview.py", "Absorption · DPMO · bands"),
    ("🏢", "Competition & Land", "pages/2_Competition_Intelligence.py", "RERA · land · margin"),
    ("👥", "Buyer Intelligence", "pages/3_Buyer_Analytics.py", "Who is booking"),
    ("📣", "Marketing Intelligence", "pages/4_Marketing_Intelligence.py", "ROI · weekly allocator"),
    ("🔬", "DMAIC Quality", "pages/5_DMAIC_Workspace.py", "Define → Control"),
    ("🏗️", "Project Deep Dive", "pages/6_Builder_Deep_Dive.py", "Project risk + ML"),
    ("🕹️", "Digital Twin", "pages/7_Digital_Twin.py", "Rival cannibalization"),
    ("💡", "AI Recommendations", "pages/8_AI_Recommendations.py", "Prescribe actions"),
    ("📉", "SPC Control", "pages/9_SPC_Control_Chart.py", "Control chart"),
    ("🗺️", "Map Intelligence", "pages/10_Map_Decision_Support.py", "Where to build"),
    ("📄", "Reports", "pages/11_Executive_Reports.py", "Board PDF pack"),
    ("🔮", "Demand Forecast", "pages/12_Forecasting.py", "Demand outlook"),
]


def _go(label: str, path: str) -> None:
    st.session_state["dss_nav_label"] = label
    st.session_state["dss_nav_label_committed"] = label
    st.session_state["dss_nav_target"] = path
    st.session_state["dss_module_nav"] = label
    st.switch_page(path)


def render_touch_hub(*, title: str = "Tap a workspace") -> None:
    """Big graphical tiles — primary phone/desktop navigation after login."""
    current = _current_nav_label()
    st.html(
        f'<div class="iq-touch-hub-title">{html.escape(title)}</div>'
        '<p class="iq-touch-hub-sub">Tap Open — each tile jumps to a live decision workspace</p>'
    )
    row: list = []
    for item in TOUCH_TILES:
        row.append(item)
        if len(row) == 3:
            _tile_row(row, current)
            row = []
    if row:
        while len(row) < 3:
            row.append(("", "", "", ""))
        _tile_row(row, current)


def _tile_row(items: list[tuple[str, str, str, str]], current: str) -> None:
    cols = st.columns(3, gap="small")
    for col, (mark, label, path, blurb) in zip(cols, items):
        with col:
            if not path:
                st.write("")
                continue
            active = label == current or Path(path).name == Path(
                dict(MODULE_NAV).get(current, "")
            ).name
            st.html(
                f'<div class="iq-tile-preview {"iq-tile-active" if active else ""}">'
                f'<span class="iq-tile-mark">{html.escape(mark)}</span>'
                f"<strong>{html.escape(label)}</strong>"
                f'<span class="iq-tile-blurb">{html.escape(blurb)}</span>'
                f"</div>"
            )
            if st.button(
                ("✓ " if active else "") + f"Open {label.split()[0]}",
                key=f"touch_tile_{path}",
                type="primary" if active else "secondary",
                width="stretch",
            ):
                _go(label, path)


def render_sidebar_touch_nav() -> None:
    """Sidebar finger-friendly jump list (replaces Streamlit's raw page list)."""
    st.sidebar.markdown("##### Workspaces")
    current = _current_nav_label()
    for label, path in MODULE_NAV:
        is_here = label == current
        clicked = st.sidebar.button(
            ("● " if is_here else "") + label,
            key=f"side_nav_{Path(path).stem}",
            type="primary" if is_here else "secondary",
            width="stretch",
            disabled=is_here,
        )
        if clicked and not is_here:
            _go(label, path)
