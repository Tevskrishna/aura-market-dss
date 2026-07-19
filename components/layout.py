"""UI chrome — theme injection, auth gate, heroes, section labels."""
from __future__ import annotations

import html
from pathlib import Path

import streamlit as st

from config import settings
from config.auth import SESSION_AUTH_KEY, SESSION_USER_KEY, verify_credentials

CSS_PATH = settings.ASSETS_DIR / "styles.css"

# Mobile-safe module jump list (does not rely on the Streamlit sidebar)
# Executive Hub first — evidence modules nested by label (P0-2)
MODULE_NAV: list[tuple[str, str]] = [
    ("Executive Hub", "app.py"),
    ("Market Intelligence", "pages/1_Market_Overview.py"),
    ("Competition & Land", "pages/2_Competition_Intelligence.py"),
    ("Buyer Intelligence", "pages/3_Buyer_Analytics.py"),
    ("Marketing Intelligence", "pages/4_Marketing_Intelligence.py"),
    ("DMAIC Quality", "pages/5_DMAIC_Workspace.py"),
    ("Project Deep Dive", "pages/6_Builder_Deep_Dive.py"),
    ("Digital Twin", "pages/7_Digital_Twin.py"),
    ("AI Recommendations", "pages/8_AI_Recommendations.py"),
    ("SPC Control", "pages/9_SPC_Control_Chart.py"),
    ("Map Intelligence", "pages/10_Map_Decision_Support.py"),
    ("Reports", "pages/11_Executive_Reports.py"),
    ("Demand Forecast", "pages/12_Forecasting.py"),
]


def inject_theme() -> None:
    chunks: list[str] = []
    for name in ("styles.css", "dynamic.css", "copilot.css", "design_tokens.css"):
        path = settings.ASSETS_DIR / name
        if path.exists():
            chunks.append(path.read_text(encoding="utf-8"))
    if chunks:
        st.html(f"<style>{''.join(chunks)}</style>")


def _running_under_pages() -> bool:
    """True when Streamlit is executing a pages/*.py script (deep link)."""
    import inspect

    for fr in inspect.stack():
        fname = fr.filename.replace("\\", "/")
        if "/pages/" in fname and fname.endswith(".py"):
            return True
    return False


def require_login() -> dict:
    inject_theme()
    if st.session_state.get(SESSION_AUTH_KEY) and st.session_state.get(SESSION_USER_KEY):
        _sidebar_chrome()
        render_module_nav()
        return st.session_state[SESSION_USER_KEY]

    # P0-3: deep-linked page URLs must not show login collage under wrong title
    if _running_under_pages():
        st.session_state["_login_notice"] = True
        try:
            st.switch_page("app.py")
        except Exception:
            st.warning("Please sign in from **Executive Hub** (Home).")
            if st.button("Go to sign-in", type="primary", width="stretch"):
                st.switch_page("app.py")
        st.stop()
        return {}

    from components.media import data_uri

    night = data_uri("hero-bengaluru-night.jpg")
    day = data_uri("hero-bagaluru-day.jpg")
    st.html(
        f"""
        <style>
          .prop-login {{
            position: relative;
            min-height: 88vh;
            border-radius: 18px;
            overflow: hidden;
            border: 1px solid #30363d;
            margin: 0.2rem 0 1rem;
            background:
              linear-gradient(105deg, rgba(8,10,14,0.92) 28%, rgba(8,10,14,0.55) 55%, rgba(8,10,14,0.25) 100%),
              url('{night}') center/cover no-repeat;
          }}
          .prop-login-grid {{
            display: grid;
            grid-template-columns: 1.15fr 0.95fr;
            gap: 1rem;
            padding: 1.4rem 1.3rem 1.5rem;
            min-height: 88vh;
            align-items: center;
          }}
          @media (max-width: 900px) {{
            .prop-login-grid {{ grid-template-columns: 1fr; min-height: auto; padding: 1rem; }}
            .prop-login {{ min-height: auto; background-position: 70% center; }}
          }}
          .prop-login-copy h1 {{
            font-size: clamp(1.7rem, 4vw, 2.4rem) !important;
            margin: 0.25rem 0 0.55rem !important;
            color: #fff !important;
            text-shadow: 0 8px 28px rgba(0,0,0,0.45);
          }}
          .prop-login-copy p {{
            color: #d7dee8 !important;
            font-size: 1rem;
            line-height: 1.5;
            max-width: 36rem;
          }}
          .prop-thumb {{
            margin-top: 1rem;
            width: min(420px, 100%);
            border-radius: 14px;
            border: 1px solid rgba(255,255,255,0.18);
            box-shadow: 0 16px 40px rgba(0,0,0,0.4);
          }}
          .prop-login-card {{
            background: rgba(22,27,34,0.88);
            backdrop-filter: blur(14px);
            border: 1px solid rgba(255,255,255,0.12);
            border-radius: 16px;
            padding: 1.15rem 1.15rem 0.85rem;
            box-shadow: 0 20px 50px rgba(0,0,0,0.45);
          }}
          .prop-login-card h3 {{
            margin: 0 0 0.35rem !important;
            color: #fff !important;
            font-size: 1.2rem !important;
          }}
        </style>
        <div class="prop-login">
          <div class="prop-login-grid">
            <div class="prop-login-copy">
              <div class="dss-kicker">BENGALURU · REAL ASSET INTELLIGENCE</div>
              <h1>Launch decisions on real market ground — not a blank terminal.</h1>
              <p>
                AURA-Market Launch Co-pilot turns Bagaluru competition, inventory, and marketing signal
                into a GO / HOLD / NO-GO call before brochure print.
              </p>
              <img class="prop-thumb" src="{day}" alt="Bagaluru residential project" />
            </div>
            <div class="prop-login-card">
              <div class="dss-brand-mark">AM</div>
              <h3>Sign in · Executive Hub</h3>
              <p class="dss-subtitle" style="margin:0 0 0.4rem;">RealEstateIQ preview · AURA-Market engine</p>
            </div>
          </div>
        </div>
        """
    )

    # Form aligned under the glass card column on desktop via nested columns
    _left, right = st.columns([1.15, 0.95])
    with right:
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="admin or demo")
            password = st.text_input("Password", type="password", placeholder="••••••••")
            submitted = st.form_submit_button("Enter Executive Hub", width="stretch")
            if submitted:
                user = verify_credentials(username, password)
                if user:
                    st.session_state[SESSION_AUTH_KEY] = True
                    st.session_state[SESSION_USER_KEY] = user
                    st.rerun()
                st.error("Invalid credentials.")
        if st.session_state.pop("_login_notice", None):
            st.info("Sign in here first — deep links open the Executive Hub when you are logged out.")
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
        '<div class="dss-mobile-nav-label">Executive Hub · jump to any module</div>'
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
        '<p class="dss-brand-name">RealEstateIQ</p>'
        '<div class="dss-brand-sub">Executive Hub · AURA engine</div>'
        '<div class="dss-brand-tag">GO · HOLD · NO-GO decisions</div>'
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
