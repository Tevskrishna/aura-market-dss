"""UI chrome — theme injection, auth gate, heroes, section labels."""
from __future__ import annotations

import html

import streamlit as st

from config import settings
from config.auth import SESSION_AUTH_KEY, SESSION_USER_KEY, verify_credentials

CSS_PATH = settings.ASSETS_DIR / "styles.css"


def inject_theme() -> None:
    css = CSS_PATH.read_text(encoding="utf-8") if CSS_PATH.exists() else ""
    st.html(f"<style>{css}</style>")


def require_login() -> dict:
    inject_theme()
    if st.session_state.get(SESSION_AUTH_KEY) and st.session_state.get(SESSION_USER_KEY):
        _sidebar_chrome()
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

    left, center, right = st.columns([1, 1.35, 1])
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


def _sidebar_chrome() -> None:
    user = st.session_state.get(SESSION_USER_KEY) or {}
    st.sidebar.html(
        f'<div class="dss-brand">'
        f'<div class="dss-brand-mark">{html.escape(settings.BRAND_MARK)}</div>'
        '<p class="dss-brand-name">AI Map Dashboard</p>'
        '<div class="dss-brand-sub">Bengaluru Real Estate</div>'
        '<div class="dss-brand-tag">AI-Powered Construction Suitability</div>'
        "</div>"
        f'<div class="dss-user-card"><strong>{html.escape(str(user.get("name", "User")))}</strong><br/>'
        f'<span>{html.escape(str(user.get("role", "viewer")).upper())} ACCESS</span></div>'
    )
    if st.sidebar.button("Sign out", width="stretch"):
        st.session_state[SESSION_AUTH_KEY] = False
        st.session_state[SESSION_USER_KEY] = None
        st.rerun()
    st.sidebar.markdown("---")


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
