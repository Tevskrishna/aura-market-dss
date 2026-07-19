"""
Touch-first module navigation — graphical tiles + sidebar buttons.
Streamlit's auto pages list is hidden; these controls are the only jump UX.
"""
from __future__ import annotations

import html

import streamlit as st

from components.layout import MODULE_NAV, _current_nav_label


# Visual hub tiles: (emoji/icon mark, short label, path, one-liner)
TOUCH_TILES: list[tuple[str, str, str, str]] = [
    ("🎯", "Executive Hub", "app.py", "GO / HOLD / NO-GO threat score"),
    ("📈", "Market", "pages/1_Market_Overview.py", "Absorption · DPMO · bands"),
    ("🏢", "Competition", "pages/2_Competition_Intelligence.py", "RERA · land · margin"),
    ("👥", "Buyers", "pages/3_Buyer_Analytics.py", "Who is booking"),
    ("📣", "Marketing", "pages/4_Marketing_Intelligence.py", "ROI · weekly allocator"),
    ("🔬", "DMAIC", "pages/5_DMAIC_Workspace.py", "Define → Control"),
    ("🏗️", "Builder", "pages/6_Builder_Deep_Dive.py", "Project risk + ML"),
    ("🕹️", "Digital Twin", "pages/7_Digital_Twin.py", "Rival cannibalization"),
    ("💡", "AI Recs", "pages/8_AI_Recommendations.py", "Prescribe actions"),
    ("📉", "SPC", "pages/9_SPC_Control_Chart.py", "Control chart"),
    ("🗺️", "Map", "pages/10_Map_Decision_Support.py", "Where to build"),
    ("📄", "Reports", "pages/11_Executive_Reports.py", "Board PDF pack"),
    ("🔮", "Forecast", "pages/12_Forecasting.py", "Demand outlook"),
]


def render_touch_hub(*, title: str = "Tap a workspace") -> None:
    """Big graphical tiles — primary phone/desktop navigation after login."""
    current = _current_nav_label()
    path_by_label = dict(MODULE_NAV)
    # Map short tile labels back via path
    st.html(
        f'<div class="iq-touch-hub-title">{html.escape(title)}</div>'
        '<p class="iq-touch-hub-sub">Graphical launch pad · works with finger + mouse</p>'
    )
    # 3-up on desktop, wraps on phone via CSS
    row: list = []
    for mark, label, path, blurb in TOUCH_TILES:
        row.append((mark, label, path, blurb))
        if len(row) == 3:
            _tile_row(row, current, path_by_label)
            row = []
    if row:
        # pad to 3 for alignment
        while len(row) < 3:
            row.append(("", "", "", ""))
        _tile_row(row, current, path_by_label)


def _tile_row(
    items: list[tuple[str, str, str, str]],
    current: str,
    path_by_label: dict[str, str],
) -> None:
    cols = st.columns(3, gap="small")
    for col, (mark, label, path, blurb) in zip(cols, items):
        with col:
            if not path:
                st.write("")
                continue
            # highlight if this path matches current module
            active = path_by_label.get(current, "") == path or (
                current.lower().startswith(label.lower()[:4]) if label else False
            )
            # also match by filename
            try:
                from pathlib import Path

                cur_path = path_by_label.get(current, "")
                active = Path(cur_path).name == Path(path).name
            except Exception:
                pass
            st.html(
                f'<div class="iq-tile-preview {"iq-tile-active" if active else ""}">'
                f'<span class="iq-tile-mark">{html.escape(mark)}</span>'
                f'<strong>{html.escape(label)}</strong>'
                f'<span class="iq-tile-blurb">{html.escape(blurb)}</span>'
                f"</div>"
            )
            if st.button(
                f"Open {label}",
                key=f"touch_tile_{path}",
                type="primary" if active else "secondary",
                width="stretch",
            ):
                st.switch_page(path)


def render_sidebar_touch_nav() -> None:
    """Sidebar finger-friendly jump list (replaces Streamlit's raw page list)."""
    st.sidebar.markdown("##### Workspaces")
    current = _current_nav_label()
    path_by = dict(MODULE_NAV)
    for label, path in MODULE_NAV:
        is_here = label == current
        if st.sidebar.button(
            ("● " if is_here else "○ ") + label,
            key=f"side_nav_{path}",
            type="primary" if is_here else "secondary",
            width="stretch",
        ):
            if not is_here:
                st.switch_page(path)
