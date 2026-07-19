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

# Sidebar IA — ≤7 sections, same 13 routes (CEO Morning Loop)
NAV_SECTIONS: list[tuple[str, list[str]]] = [
    ("Executive Decision", ["Executive Hub", "Reports"]),
    ("Market & Land", ["Market Intelligence", "Competition & Land", "Map Intelligence"]),
    ("Customers & Growth", ["Buyer Intelligence", "Marketing Intelligence"]),
    ("Simulate & Act", ["Digital Twin", "AI Recommendations", "Demand Forecast"]),
    ("Quality Evidence", ["DMAIC Quality", "Project Deep Dive", "SPC Control"]),
]


def inject_theme(*, gate: bool = False) -> None:
    chunks: list[str] = []
    for name in ("styles.css", "dynamic.css", "copilot.css", "design_tokens.css", "realtime_hud.css"):
        path = settings.ASSETS_DIR / name
        if path.exists():
            chunks.append(path.read_text(encoding="utf-8"))
    # Hide Streamlit auto multipage list — causes login hell + raw UX
    chunks.append(
        """
        [data-testid="stSidebarNav"],
        [data-testid="stSidebarNavItems"],
        div[data-testid="stSidebarNav"] {
          display: none !important;
          height: 0 !important;
          overflow: hidden !important;
          visibility: hidden !important;
        }
        """
    )
    if gate:
        chunks.append(
            """
            section[data-testid="stSidebar"] { display: none !important; }
            [data-testid="stSidebarCollapsedControl"] { display: none !important; }
            header[data-testid="stHeader"] {
              background: transparent !important;
            }
            .block-container {
              padding-top: 0.75rem !important;
              max-width: 1100px !important;
            }
            div[data-testid="stForm"] input {
              min-height: 48px !important;
              font-size: 1.05rem !important;
            }
            div[data-testid="stForm"] button[kind="primaryFormSubmit"],
            div[data-testid="stForm"] button {
              min-height: 52px !important;
              font-size: 1.05rem !important;
              font-weight: 800 !important;
            }
            """
        )
    st.html(f"<style>{''.join(chunks)}</style>")


def _running_under_pages() -> bool:
    """True when Streamlit is executing a pages/*.py script (deep link)."""
    import inspect

    for fr in inspect.stack():
        fname = fr.filename.replace("\\", "/")
        if "/pages/" in fname and fname.endswith(".py"):
            return True
    return False


def require_login(active_module: str | None = None) -> dict:
    """
    Auth gate. Pass active_module (exact MODULE_NAV label) so sidebar/hub
    highlight the real page — critical on Streamlit Cloud deep links.
    """
    if active_module:
        st.session_state["dss_nav_label"] = active_module
        st.session_state["dss_nav_label_committed"] = active_module
        for label, path in MODULE_NAV:
            if label == active_module:
                st.session_state["dss_nav_target"] = path
                break

    if st.session_state.get(SESSION_AUTH_KEY) and st.session_state.get(SESSION_USER_KEY):
        inject_theme(gate=False)
        _sidebar_chrome()
        from components.touch_nav import render_sidebar_touch_nav

        render_sidebar_touch_nav()
        render_module_nav()
        return st.session_state[SESSION_USER_KEY]

    inject_theme(gate=True)

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
            min-height: 92vh;
            border-radius: 20px;
            overflow: hidden;
            border: 1px solid #30363d;
            margin: 0;
            background:
              linear-gradient(105deg, rgba(8,10,14,0.94) 22%, rgba(8,10,14,0.55) 55%, rgba(8,10,14,0.2) 100%),
              url('{night}') center/cover no-repeat;
          }}
          .prop-login-grid {{
            display: grid;
            grid-template-columns: 1.1fr 0.9fr;
            gap: 1.25rem;
            padding: clamp(1.2rem, 3vw, 2rem);
            min-height: 92vh;
            align-items: center;
          }}
          @media (max-width: 900px) {{
            .prop-login-grid {{ grid-template-columns: 1fr; min-height: auto; padding: 1rem; }}
            .prop-login {{ min-height: auto; background-position: 70% center; }}
            .prop-thumb {{ display: none; }}
          }}
          .prop-login-copy .prop-brand {{
            margin: 0 0 0.35rem !important;
            font-size: clamp(2.3rem, 6vw, 3.5rem) !important;
            font-weight: 800 !important;
            letter-spacing: -0.03em;
            line-height: 1.05 !important;
            color: #fff !important;
            text-shadow: 0 10px 32px rgba(0,0,0,0.5);
          }}
          .prop-login-copy .prop-brand span {{ color: #ff4b4b; }}
          .prop-login-copy h1 {{
            font-size: clamp(1.15rem, 2.6vw, 1.55rem) !important;
            font-weight: 600 !important;
            margin: 0.15rem 0 0.65rem !important;
            color: #e8eef6 !important;
            line-height: 1.35 !important;
            max-width: 34rem;
          }}
          .prop-login-copy .prop-place {{
            display: inline-block;
            margin: 0 0 0.55rem;
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            color: #9aa7b5;
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
            background: rgba(22,27,34,0.92);
            backdrop-filter: blur(16px);
            border: 1px solid rgba(255,255,255,0.14);
            border-radius: 18px;
            padding: 1.35rem 1.25rem 0.5rem;
            box-shadow: 0 24px 60px rgba(0,0,0,0.5);
          }}
          .prop-login-card h3 {{
            margin: 0 0 0.35rem !important;
            color: #fff !important;
            font-size: 1.35rem !important;
          }}
          .prop-feature-row {{
            display: flex; flex-wrap: wrap; gap: 0.45rem; margin: 0.85rem 0 0.2rem;
          }}
          .prop-feature-row span {{
            border: 1px solid rgba(255,255,255,0.14);
            background: rgba(255,255,255,0.05);
            color: #c9d1d9;
            border-radius: 999px;
            padding: 0.35rem 0.7rem;
            font-size: 0.72rem;
            font-weight: 700;
          }}
        </style>
        <div class="prop-login">
          <div class="prop-login-grid">
            <div class="prop-login-copy">
              <div class="prop-brand">AURA<span>-Market</span></div>
              <div class="prop-place">Bagaluru · Launch Decision Co-pilot</div>
              <h1>GO / HOLD / NO-GO before brochure print — not a blank terminal.</h1>
              <p>
                Competition, land margin, inventory twin, and marketing ROI fold into one
                executive call for the Aerospace Highway corridor.
              </p>
              <div class="prop-feature-row">
                <span>Touch module hub</span><span>Live threat score</span><span>Board PDF</span>
              </div>
              <img class="prop-thumb" src="{day}" alt="Bagaluru residential project" />
            </div>
            <div class="prop-login-card">
              <div class="dss-brand-mark">AM</div>
              <h3>Sign in · Executive Hub</h3>
              <p class="dss-subtitle" style="margin:0 0 0.55rem;">One gate — then a graphical workspace. Sidebar page list is hidden.</p>
            </div>
          </div>
        </div>
        """
    )

    _left, right = st.columns([1.1, 0.9])
    with right:
        with st.form("login_form", clear_on_submit=False):
            username = st.text_input("Username", placeholder="admin or demo")
            password = st.text_input("Password", type="password", placeholder="••••••••")
            submitted = st.form_submit_button("Enter Executive Hub →", type="primary", width="stretch")
            if submitted:
                user = verify_credentials(username, password)
                if user:
                    st.session_state[SESSION_AUTH_KEY] = True
                    st.session_state[SESSION_USER_KEY] = user
                    st.rerun()
                st.error("Invalid credentials.")
        if st.session_state.pop("_login_notice", None):
            st.info("Sign in once here — module links stay locked until you enter the Hub.")
        st.html(
            '<div class="dss-login-creds">Demo · <b>admin / admin123</b> &nbsp;·&nbsp; <b>demo / demo123</b></div>'
        )
    st.stop()
    return {}


def _current_nav_label() -> str:
    """Best-effort match of the running script to MODULE_NAV labels."""
    committed = st.session_state.get("dss_nav_label_committed")
    if committed and committed in {label for label, _ in MODULE_NAV}:
        return committed

    import inspect

    for fr in inspect.stack():
        fname = fr.filename.replace("\\", "/").lower()
        for label, path in MODULE_NAV:
            pname = Path(path).name.lower()
            if fname.endswith("/" + pname) or fname.endswith(pname):
                return label
        if fname.endswith("/app.py") or fname.endswith("\\app.py"):
            return MODULE_NAV[0][0]

    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx

        ctx = get_script_run_ctx()
        raw = str(getattr(ctx, "main_script_path", "") or "").replace("\\", "/").lower()
        name = Path(raw).name.lower()
        for label, path in MODULE_NAV:
            if Path(path).name.lower() == name:
                return label
            if path.replace("\\", "/").lower() in raw:
                return label
    except Exception:
        pass
    return st.session_state.get("dss_nav_label", MODULE_NAV[0][0])


def render_module_nav() -> None:
    """Top jump list — switches ONLY when the user changes the selectbox."""
    from components.touch_nav import apply_pending_module_nav

    apply_pending_module_nav()

    labels = [label for label, _ in MODULE_NAV]
    path_by = dict(MODULE_NAV)
    current = _current_nav_label()
    if current not in labels:
        current = labels[0]

    if "dss_module_nav" not in st.session_state:
        st.session_state["dss_module_nav"] = current
    elif st.session_state.get("dss_nav_label_committed") and st.session_state[
        "dss_module_nav"
    ] != st.session_state["dss_nav_label_committed"]:
        # Keep widget in sync when page was opened via sidebar / tile (pre-widget only)
        st.session_state["dss_module_nav"] = st.session_state["dss_nav_label_committed"]

    st.html(
        '<div class="dss-mobile-nav">'
        '<div class="dss-mobile-nav-label">Jump</div>'
        "</div>"
    )

    def _on_nav_change() -> None:
        label = st.session_state.get("dss_module_nav")
        if not label or label not in path_by:
            return
        st.session_state["dss_nav_label"] = label
        st.session_state["dss_nav_label_committed"] = label
        st.session_state["dss_nav_target"] = path_by[label]
        st.switch_page(path_by[label])

    st.selectbox(
        "Go to module",
        labels,
        key="dss_module_nav",
        label_visibility="collapsed",
        on_change=_on_nav_change,
        help="Change module. Prefer sidebar Workspaces or Hub tiles.",
    )


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
    st.sidebar.caption("Workspaces · page list hidden")


def page_hero(
    kicker: str,
    title: str,
    subtitle: str = "",
    chips: list[tuple[str, str]] | None = None,
    *,
    compact: bool = False,
) -> None:
    """Supporting chrome. Use compact=True under EDS so the sheet stays primary."""
    if compact:
        sub = f'<p class="dss-subtitle dss-hero-compact-sub">{html.escape(subtitle)}</p>' if subtitle else ""
        st.html(
            f'<div class="dss-hero dss-hero-compact">'
            f'<div class="dss-kicker">{html.escape(kicker)}</div>'
            f"<h1>{html.escape(title)}</h1>"
            f"{sub}</div>"
        )
        return
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
