"""
Touch-first module navigation — graphical tiles + sidebar buttons.
"""
from __future__ import annotations

import html
from pathlib import Path

import streamlit as st

from components.nav_config import (
    IC_DEMO_LABELS,
    MODULE_NAV,
    modules_for_mode,
    sections_for_mode,
)

PENDING_MODULE_NAV = "_dss_pending_module_nav"

TOUCH_TILES: list[tuple[str, str, str, str]] = [
    ("🎯", "Executive Hub", "app.py", "Should we launch?"),
    ("📈", "Market Intelligence", "pages/1_Market_Overview.py", "Is demand healthy?"),
    ("🏢", "Competition & Land", "pages/2_Competition_Intelligence.py", "Will competitors hurt us?"),
    ("👥", "Buyer Intelligence", "pages/3_Buyer_Analytics.py", "Who will buy?"),
    ("📣", "Marketing Intelligence", "pages/4_Marketing_Intelligence.py", "Can marketing hit target?"),
    ("🔬", "DMAIC Quality", "pages/5_DMAIC_Workspace.py", "Why are problems occurring?"),
    ("🏗️", "Project Deep Dive", "pages/6_Builder_Deep_Dive.py", "Is the project healthy?"),
    ("📊", "Scenario Engine", "pages/7_Digital_Twin.py", "What if strategy changes?"),
    ("💡", "Decision Explanation", "pages/8_AI_Recommendations.py", "Why did Hub decide this?"),
    ("📉", "SPC Control", "pages/9_SPC_Control_Chart.py", "Can we trust this?"),
    ("🗺️", "Map Intelligence", "pages/10_Map_Decision_Support.py", "Where to build?"),
    ("📄", "Reports", "pages/11_Executive_Reports.py", "Board decision pack"),
    ("🔮", "Demand Forecast", "pages/12_Forecasting.py", "Near-term outlook"),
]


def ic_demo_mode() -> bool:
    return bool(st.session_state.get("iq_ic_demo_mode", True))


def apply_pending_module_nav() -> None:
    pending = st.session_state.pop(PENDING_MODULE_NAV, None)
    if pending is not None:
        st.session_state["dss_module_nav"] = pending


def navigate_to(label: str, path: str) -> None:
    st.session_state["dss_nav_label"] = label
    st.session_state["dss_nav_label_committed"] = label
    st.session_state["dss_nav_target"] = path
    st.session_state[PENDING_MODULE_NAV] = label
    st.switch_page(path)


def _current_nav_label() -> str:
    from components.layout import _current_nav_label as _cnl

    return _cnl()


def render_touch_hub(*, title: str = "Tap a workspace") -> None:
    current = _current_nav_label()
    ic = ic_demo_mode()
    tiles = [t for t in TOUCH_TILES if (t[1] in IC_DEMO_LABELS) or not ic]
    st.html(
        f'<div class="iq-touch-hub-title">{html.escape(title)}</div>'
        f'<p class="iq-touch-hub-sub">'
        f'{"IC Demo Path — evidence that supports the Hub call" if ic else "Full Quality Lab workspaces"}'
        f"</p>"
    )
    row: list = []
    for item in tiles:
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
            )
            if clicked:
                if active:
                    try:
                        st.toast(f"Already on {label}", icon="📍")
                    except Exception:
                        pass
                else:
                    navigate_to(label, path)


def render_sidebar_touch_nav() -> None:
    st.sidebar.markdown("##### Workspaces")
    current = _current_nav_label()
    ic = ic_demo_mode()
    mods = modules_for_mode(ic_demo=ic)
    path_by = dict(mods)
    known = {label for label, _ in mods}
    for section, labels in sections_for_mode(ic_demo=ic):
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
            )
            if clicked:
                if is_here:
                    try:
                        st.toast(f"Already on {label}", icon="📍")
                    except Exception:
                        pass
                else:
                    navigate_to(label, path)
    if ic:
        st.sidebar.caption("Quality Lab pages are hidden — turn off IC Demo Mode to open them.")
