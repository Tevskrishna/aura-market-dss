"""
Touch-first module navigation — graphical tiles + sidebar buttons.
Streamlit's auto pages list is hidden; these controls are the only jump UX.

IMPORTANT: never assign `st.session_state["dss_module_nav"]` AFTER the selectbox
with that key is created in the same run — Streamlit raises StreamlitAPIException.
Use navigate_to() which stashes a pending label for the next run instead.
"""
from __future__ import annotations

import html
from pathlib import Path

import streamlit as st

from components.nav_config import MODULE_NAV, NAV_SECTIONS
from components.layout import _current_nav_label

PENDING_MODULE_NAV = "_dss_pending_module_nav"

TOUCH_TILES: list[tuple[str, str, str, str]] = [
    ("🎯", "Executive Hub", "app.py", "Should we launch?"),
    ("📈", "Market Intelligence", "pages/1_Market_Overview.py", "Is demand healthy?"),
    ("🏢", "Competition & Land", "pages/2_Competition_Intelligence.py", "Will competitors hurt us?"),
    ("👥", "Buyer Intelligence", "pages/3_Buyer_Analytics.py", "Who will buy?"),
    ("📣", "Marketing Intelligence", "pages/4_Marketing_Intelligence.py", "Can marketing hit target?"),
    ("🔬", "DMAIC Quality", "pages/5_DMAIC_Workspace.py", "Why are problems occurring?"),
    ("🏗️", "Project Deep Dive", "pages/6_Builder_Deep_Dive.py", "Is the project healthy?"),
    ("🕹️", "Digital Twin", "pages/7_Digital_Twin.py", "What if strategy changes?"),
    ("💡", "Decision Explanation", "pages/8_AI_Recommendations.py", "Why did Hub decide this?"),
    ("📉", "SPC Control", "pages/9_SPC_Control_Chart.py", "Can we trust this?"),
    ("🗺️", "Map Intelligence", "pages/10_Map_Decision_Support.py", "Where to build?"),
    ("📄", "Reports", "pages/11_Executive_Reports.py", "Board decision pack"),
    ("🔮", "Demand Forecast", "pages/12_Forecasting.py", "Near-term outlook"),
]


def apply_pending_module_nav() -> None:
    """Must run before selectbox(key='dss_module_nav') is instantiated."""
    pending = st.session_state.pop(PENDING_MODULE_NAV, None)
    if pending is not None:
        st.session_state["dss_module_nav"] = pending


def navigate_to(label: str, path: str) -> None:
    """Safe page jump — does not mutate the live selectbox widget key."""
    st.session_state["dss_nav_label"] = label
    st.session_state["dss_nav_label_committed"] = label
    st.session_state["dss_nav_target"] = path
    st.session_state[PENDING_MODULE_NAV] = label
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
    path_by = dict(MODULE_NAV)
    for col, (mark, label, path, blurb) in zip(cols, items):
        with col:
            if not path:
                st.write("")
                continue
            cur_path = path_by.get(current, "")
            active = label == current or (
                bool(cur_path) and Path(path).name == Path(cur_path).name
            )
            st.html(
                f'<div class="iq-tile-preview {"iq-tile-active" if active else ""}">'
                f'<span class="iq-tile-mark">{html.escape(mark)}</span>'
                f"<strong>{html.escape(label)}</strong>"
                f'<span class="iq-tile-blurb">{html.escape(blurb)}</span>'
                f"</div>"
            )
            clicked = st.button(
                ("You are here · " if active else "Open ") + label.split()[0],
                key=f"touch_tile_{Path(path).stem}",
                type="primary" if active else "secondary",
                width="stretch",
                disabled=active,
            )
            if clicked and not active:
                navigate_to(label, path)


def render_sidebar_touch_nav() -> None:
    """Sidebar finger-friendly jump list grouped into decision sections."""
    st.sidebar.markdown("##### Workspaces")
    current = _current_nav_label()
    path_by = dict(MODULE_NAV)
    known = {label for label, _ in MODULE_NAV}
    for section, labels in NAV_SECTIONS:
        st.sidebar.caption(section)
        for label in labels:
            if label not in known:
                continue
            path = path_by[label]
            is_here = label == current
            clicked = st.sidebar.button(
                ("● " if is_here else "") + label,
                key=f"side_nav_{Path(path).stem}",
                type="primary" if is_here else "secondary",
                width="stretch",
                disabled=is_here,
            )
            if clicked and not is_here:
                navigate_to(label, path)
