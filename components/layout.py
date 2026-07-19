"""UI chrome — theme injection, auth gate, heroes, section labels."""
from __future__ import annotations

import html
from pathlib import Path

import streamlit as st

from config import settings
from config.auth import SESSION_AUTH_KEY, SESSION_USER_KEY, verify_credentials

CSS_PATH = settings.ASSETS_DIR / "styles.css"

# Mobile-safe module jump list (does not rely on the Streamlit sidebar)
MODULE_NAV: list[tuple[str, str]] = [
    ("Launch Co-pilot", "app.py"),
    ("Market Overview", "pages/1_Market_Overview.py"),
    ("Competition Intelligence", "pages/2_Competition_Intelligence.py"),
    ("Audience Demographics", "pages/3_Buyer_Analytics.py"),
    ("Marketing Intelligence", "pages/4_Marketing_Intelligence.py"),
    ("DMAIC Workspace", "pages/5_DMAIC_Workspace.py"),
    ("Builder Deep Dive", "pages/6_Builder_Deep_Dive.py"),
    ("Digital Twin", "pages/7_Digital_Twin.py"),
    ("AI Recommendations", "pages/8_AI_Recommendations.py"),
    ("SPC Control Chart", "pages/9_SPC_Control_Chart.py"),
    ("Map Decision Support", "pages/10_Map_Decision_Support.py"),
    ("Executive Reports", "pages/11_Executive_Reports.py"),
    ("Forecasting", "pages/12_Forecasting.py"),
]


def inject_theme() -> None:
    chunks: list[str] = []
    for name in ("styles.css", "dynamic.css", "copilot.css"):
        path = settings.ASSETS_DIR / name
        if path.exists():
            chunks.append(path.read_text(encoding="utf-8"))
    if chunks:
        st.html(f"<style>{''.join(chunks)}</style>")


def require_login() -> dict:
    inject_theme()
    if st.session_state.get(SESSION_AUTH_KEY) and st.session_state.get(SESSION_USER_KEY):
        _sidebar_chrome()
        render_module_nav()
        return st.session_state[SESSION_USER_KEY]

    st.html(
        '<div class="dss-login-shell"><div class="dss-login-wrap">'
        '<div class="dss-brand-mark">AM</div>'
        '<div class="dss-kicker">AI-Powered Construction Suitability</div>'
        "<h2>AURA-Market</h2>"
        '<p class="dss-subtitle">Bengaluru Real Estate Decision Support — competition, margins, '
        "demand personas, map suitability, and launch interventions.</p>"
        "</div></div>"
    )

    _, center, _ = st.columns([0.2, 1.2, 0.2])
    with center:
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="admin or demo")
            password = st.text_input("Password", type="password", placeholder="••••••••")
            submitted = st.form_submit_button("Sign in", width="stretch")
            if submitted:
                user = verify_credentials(username, password)
                if user:
                    st.session_state[SESSION_AUTH_KEY] = True
                    st.session_state[SESSION_USER_KEY] = user
                    st.rerun()
                st.error("Invalid credentials.")
        st.html(
            '<div class="dss-login-creds">Demo · <b>admin / admin123</b> &nbsp;·&nbsp; <b>demo / demo123</b></div>'
        )
    st.stop()
    return {}


def _current_nav_label() -> str:
    """Best-effort match of the running script to MODULE_NAV labels."""
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx

        ctx = get_script_run_ctx()
        raw = str(getattr(ctx, "main_script_path", "") or "")
        name = Path(raw.replace("\\", "/")).name.lower()
        for label, path in MODULE_NAV:
            if Path(path).name.lower() == name:
                return label
            if path.replace("\\", "/").lower() in raw.replace("\\", "/").lower():
                return label
    except Exception:
        pass
    return st.session_state.get("dss_nav_label", MODULE_NAV[0][0])


def render_module_nav() -> None:
    """Top-of-page module switcher — works when the sidebar cannot be opened on mobile."""
    labels = [label for label, _ in MODULE_NAV]
    path_by = dict(MODULE_NAV)
    current = _current_nav_label()
    if current not in labels:
        current = labels[0]
    idx = labels.index(current)

    st.html(
        '<div class="dss-mobile-nav">'
        '<div class="dss-mobile-nav-label">Modules · tap to open any page (mobile friendly)</div>'
        "</div>"
    )
    choice = st.selectbox(
        "Go to module",
        labels,
        index=idx,
        key="dss_module_nav",
        label_visibility="collapsed",
        help="Use this if the left sidebar is closed on your phone. On desktop you can also use the sidebar.",
    )
    st.session_state["dss_nav_label"] = choice
    target = path_by[choice]
    prev = st.session_state.get("dss_nav_target")
    if prev is None:
        st.session_state["dss_nav_target"] = target
    elif target != prev:
        st.session_state["dss_nav_target"] = target
        st.switch_page(target)


def _sidebar_chrome() -> None:
    user = st.session_state.get(SESSION_USER_KEY) or {}
    st.sidebar.html(
        f'<div class="dss-brand">'
        f'<div class="dss-brand-mark">{html.escape(settings.BRAND_MARK)}</div>'
        '<p class="dss-brand-name">Launch Co-pilot</p>'
        '<div class="dss-brand-sub">Bengaluru Real Estate</div>'
        '<div class="dss-brand-tag">GO · HOLD · NO-GO in one screen</div>'
        "</div>"
        f'<div class="dss-user-card"><strong>{html.escape(str(user.get("name", "User")))}</strong><br/>'
        f'<span>{html.escape(str(user.get("role", "viewer")).upper())} ACCESS</span></div>'
    )
    if st.sidebar.button("Sign out", width="stretch"):
        st.session_state[SESSION_AUTH_KEY] = False
        st.session_state[SESSION_USER_KEY] = None
        st.rerun()
    st.sidebar.markdown("---")
    st.sidebar.caption("Phone tip: use the red menu button top-left, or the Modules dropdown on the page.")


def page_hero(
    kicker: str,
    title: str,
    subtitle: str,
    chips: list[tuple[str, str]] | None = None,
) -> None:
    chips = chips or []
    chip_html = "".join(
        f'<span class="dss-chip {html.escape(klass)}">{html.escape(label)}</span>'
        for label, klass in chips
    )
    st.html(
        f'<div class="dss-hero">'
        f'<div class="dss-kicker">{html.escape(kicker)}</div>'
        f"<h1>{html.escape(title)}</h1>"
        f'<p class="dss-subtitle">{html.escape(subtitle)}</p>'
        f'<div class="dss-chip-row">{chip_html}</div></div>'
    )


def section_label(title: str) -> None:
    st.html(f'<div class="dss-section-label"><h2>{html.escape(title)}</h2></div>')


def info_panel(title: str, body: str) -> None:
    st.html(
        f'<div class="dss-panel"><h4>{html.escape(title)}</h4>'
        f"<p>{html.escape(body)}</p></div>"
    )


def module_cards(modules: list[tuple[str, str, str]]) -> None:
    """modules: (index, title, description)"""
    cards = []
    for idx, title, desc in modules:
        cards.append(
            f'<div class="dss-module">'
            f'<div class="dss-module-index">{html.escape(idx)}</div>'
            f"<strong>{html.escape(title)}</strong>"
            f"<span>{html.escape(desc)}</span></div>"
        )
    st.html(f'<div class="dss-module-grid">{"".join(cards)}</div>')


def decision_action(title: str, actions: list[str], tone: str = "action") -> None:
    """Explicit 'what should the developer do?' callout — required on every module."""
    items = "".join(f"<li>{html.escape(a)}</li>" for a in actions if a)
    klass = {"ok": "ok", "warn": "warn", "action": ""}.get(tone, "")
    st.html(
        f'<div class="dss-decision {klass}">'
        f'<div class="dss-decision-kicker">Developer action</div>'
        f"<h3>{html.escape(title)}</h3>"
        f"<ul>{items}</ul></div>"
    )
