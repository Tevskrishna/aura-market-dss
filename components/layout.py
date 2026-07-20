"""UI chrome — theme injection, auth gate, heroes, section labels."""
from __future__ import annotations

import html
from pathlib import Path

import streamlit as st

from config import settings
from config.auth import SESSION_AUTH_KEY, SESSION_USER_KEY, verify_credentials
from components.nav_config import MODULE_NAV, NAV_SECTIONS

CSS_PATH = settings.ASSETS_DIR / "styles.css"

# Re-export for any `from components.layout import MODULE_NAV` callers
__all__ = ["MODULE_NAV", "NAV_SECTIONS"]


def inject_theme(*, gate: bool = False) -> None:
    chunks: list[str] = []
    for name in (
        "styles.css",
        "dynamic.css",
        "copilot.css",
        "design_tokens.css",
        "realtime_hud.css",
        "mobile.css",
    ):
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
              padding-top: 0.5rem !important;
              max-width: 1240px !important;
            }
            div[data-testid="stForm"] {
              background: rgba(10, 14, 22, 0.72);
              border: 1px solid rgba(61, 224, 208, 0.2);
              border-radius: 14px;
              padding: 1rem 1.1rem 0.85rem;
              backdrop-filter: blur(14px);
              box-shadow: 0 20px 50px rgba(0,0,0,0.4);
              margin-top: -4.5rem;
              position: relative;
              z-index: 5;
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
            .dss-login-creds {
              margin-top: 0.65rem;
              color: #8a9bb0;
              font-size: 0.85rem;
            }
            @media (max-width: 900px) {
              div[data-testid="stForm"] { margin-top: 0.5rem; }
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
        from components.ai_copilot import render_ai_copilot, render_sound_pref
        from components.product_tour import render_product_tour, start_tour_replay

        render_sound_pref()
        if st.sidebar.button("Replay product tour", width="stretch", key="iq_replay_tour"):
            start_tour_replay()
            st.rerun()
        render_ai_copilot()
        from components.live_presence import render_live_presence, render_mobile_dock

        render_product_tour()
        render_live_presence()
        render_mobile_dock()
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
          .iq-gate {{
            position: relative;
            min-height: min(88vh, 820px);
            border-radius: 16px;
            overflow: hidden;
            margin: 0 0 0.75rem;
            border: 1px solid rgba(61, 224, 208, 0.2);
            background:
              radial-gradient(900px 420px at 15% 20%, rgba(255, 138, 26, 0.18), transparent 55%),
              radial-gradient(700px 380px at 85% 70%, rgba(61, 224, 208, 0.12), transparent 50%),
              linear-gradient(115deg, rgba(5,7,10,0.94) 0%, rgba(5,7,10,0.55) 48%, rgba(5,7,10,0.25) 100%),
              url('{night}') 62% center / cover no-repeat;
            box-shadow: 0 28px 80px rgba(0,0,0,0.55);
            perspective: 1400px;
          }}
          .iq-gate-grid {{
            display: grid;
            grid-template-columns: 1.15fr 0.85fr;
            gap: clamp(1rem, 3vw, 2rem);
            padding: clamp(1.25rem, 3.5vw, 2.4rem);
            min-height: min(88vh, 820px);
            align-items: center;
            position: relative;
            z-index: 1;
          }}
          @media (max-width: 900px) {{
            .iq-gate {{ min-height: auto; }}
            .iq-gate-grid {{ grid-template-columns: 1fr; min-height: auto; padding: 1.1rem; }}
            .iq-gate-float {{ display: none; }}
          }}
          .iq-gate-kicker {{
            font-family: "Exo 2", sans-serif;
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.18em;
            text-transform: uppercase;
            color: #ffc048;
            margin-bottom: 0.55rem;
          }}
          .iq-gate-brand {{
            margin: 0 0 0.35rem !important;
            font-family: "Exo 2", sans-serif !important;
            font-size: clamp(2.4rem, 6.2vw, 3.6rem) !important;
            font-weight: 800 !important;
            letter-spacing: -0.03em;
            line-height: 1.02 !important;
            color: #fff !important;
            text-shadow: 0 12px 40px rgba(0,0,0,0.45);
          }}
          .iq-gate-brand span {{
            background: linear-gradient(90deg, #ffc048, #ff8a1a);
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent;
          }}
          .iq-gate-subbrand {{
            font-size: 0.82rem;
            color: #8a9bb0;
            margin-bottom: 0.85rem;
            letter-spacing: 0.04em;
          }}
          .iq-gate-copy h1 {{
            font-family: "Exo 2", sans-serif !important;
            font-size: clamp(1.2rem, 2.8vw, 1.65rem) !important;
            font-weight: 700 !important;
            margin: 0 0 0.7rem !important;
            color: #f2f6fb !important;
            line-height: 1.28 !important;
            max-width: 36rem;
          }}
          .iq-gate-copy p {{
            color: #c5d0dc !important;
            font-size: 1.02rem;
            line-height: 1.55;
            max-width: 38rem;
            margin: 0 0 1rem !important;
          }}
          .iq-gate-pills {{
            display: flex; flex-wrap: wrap; gap: 0.45rem; margin: 0 0 1.1rem;
          }}
          .iq-gate-pills span {{
            border: 1px solid rgba(61, 224, 208, 0.28);
            background: rgba(8, 14, 22, 0.55);
            color: #d7e6ef;
            border-radius: 6px;
            padding: 0.4rem 0.75rem;
            font-size: 0.72rem;
            font-weight: 700;
            font-family: "Exo 2", sans-serif;
            letter-spacing: 0.04em;
          }}
          .iq-gate-stage {{
            position: relative;
            width: min(460px, 100%);
            height: 220px;
            margin-top: 0.35rem;
            transform-style: preserve-3d;
          }}
          .iq-gate-float {{
            position: absolute;
            border-radius: 12px;
            border: 1px solid rgba(255,255,255,0.16);
            box-shadow: 0 22px 50px rgba(0,0,0,0.45);
            overflow: hidden;
            background: #0a0e14;
          }}
          .iq-gate-float img {{
            display: block;
            width: 100%;
            height: 100%;
            object-fit: cover;
          }}
          .iq-gate-float-a {{
            width: 78%;
            height: 170px;
            left: 0;
            top: 28px;
            transform: rotateY(8deg) rotateX(4deg) translateZ(12px);
            z-index: 1;
          }}
          .iq-gate-float-b {{
            width: 52%;
            height: 120px;
            right: 0;
            top: 0;
            transform: rotateY(-10deg) rotateX(6deg) translateZ(40px);
            z-index: 2;
            border-color: rgba(255, 192, 72, 0.35);
          }}
          .iq-gate-stat {{
            position: absolute;
            left: 8%;
            bottom: 0;
            z-index: 3;
            padding: 0.65rem 0.85rem;
            border-radius: 8px;
            background: rgba(12, 18, 28, 0.88);
            border: 1px solid rgba(61, 224, 208, 0.3);
            backdrop-filter: blur(10px);
            box-shadow: 0 12px 30px rgba(0,0,0,0.4);
            transform: translateZ(60px);
          }}
          .iq-gate-stat strong {{
            display: block;
            font-family: "Exo 2", sans-serif;
            font-size: 1.05rem;
            color: #ffc048;
          }}
          .iq-gate-stat span {{
            font-size: 0.7rem;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: #8a9bb0;
          }}
          .iq-gate-card {{
            background: rgba(10, 14, 22, 0.72);
            backdrop-filter: blur(18px);
            border: 1px solid rgba(61, 224, 208, 0.22);
            border-radius: 14px;
            padding: 1.35rem 1.25rem 1rem;
            box-shadow:
              0 28px 70px rgba(0,0,0,0.55),
              inset 0 1px 0 rgba(255,255,255,0.06);
            transform: rotateY(-4deg);
            animation: iq-gate-in 0.55s ease both;
          }}
          @keyframes iq-gate-in {{
            from {{ opacity: 0; transform: rotateY(-4deg) translateY(14px); }}
            to {{ opacity: 1; transform: rotateY(-4deg) translateY(0); }}
          }}
          .iq-gate-mark {{
            width: 2.4rem; height: 2.4rem;
            border-radius: 8px;
            display: grid; place-items: center;
            font-family: "Exo 2", sans-serif;
            font-weight: 800;
            font-size: 0.85rem;
            color: #140c04;
            background: linear-gradient(145deg, #ffc048, #ff8a1a);
            margin-bottom: 0.75rem;
            box-shadow: 0 0 20px rgba(255, 138, 26, 0.35);
          }}
          .iq-gate-card h3 {{
            margin: 0 0 0.3rem !important;
            color: #fff !important;
            font-family: "Exo 2", sans-serif !important;
            font-size: 1.35rem !important;
          }}
          .iq-gate-card .iq-gate-card-sub {{
            margin: 0 0 0.25rem !important;
            color: #8a9bb0 !important;
            font-size: 0.9rem !important;
          }}
          @media (prefers-reduced-motion: reduce) {{
            .iq-gate-card {{ animation: none; transform: none; }}
            .iq-gate-float-a, .iq-gate-float-b, .iq-gate-stat {{ transform: none; }}
          }}
        </style>
        <div class="iq-gate" role="banner">
          <div class="iq-gate-grid">
            <div class="iq-gate-copy">
              <div class="iq-gate-kicker">India · Bagaluru · Aerospace Highway</div>
              <div class="iq-gate-brand">RealEstate<span>IQ</span></div>
              <div class="iq-gate-subbrand">AURA-Market Decision Intelligence · Launch Co-pilot</div>
              <h1>GO / HOLD / NO-GO before brochure print — one executive call for the corridor.</h1>
              <p>
                Competition blind spot, land margin, inventory twin, and marketing ROI —
                composed into a living decision OS for Indian residential developers.
              </p>
              <div class="iq-gate-pills">
                <span>Executive sheet</span>
                <span>Threat score</span>
                <span>Digital twin</span>
                <span>Board pack</span>
              </div>
              <div class="iq-gate-stage" aria-hidden="true">
                <div class="iq-gate-float iq-gate-float-a"><img src="{day}" alt="" /></div>
                <div class="iq-gate-float iq-gate-float-b"><img src="{night}" alt="" /></div>
                <div class="iq-gate-stat">
                  <strong>GO · HOLD · NO-GO</strong>
                  <span>Morning decision loop</span>
                </div>
              </div>
            </div>
            <div class="iq-gate-card" id="iq-gate-signin">
              <div class="iq-gate-mark">IQ</div>
              <h3>Sign in</h3>
              <p class="iq-gate-card-sub">Enter the Executive Hub. One gate — modules unlock after.</p>
            </div>
          </div>
        </div>
        """
    )

    _left, right = st.columns([1.15, 0.85], gap="large")
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
    board = st.sidebar.toggle(
        "Board Mode",
        value=bool(st.session_state.get("iq_board_mode", False)),
        key="iq_board_mode",
        help="Presentation density — larger type, quieter chrome for IC / interview demos.",
    )
    if board:
        st.html(
            "<style>"
            "html { font-size: 110% !important; }"
            ".iq-eds,.iq-hub-ask,.copilot-gauge-wrap { box-shadow: none !important; }"
            ".dss-hero,.dss-hero-compact,.iq-honesty { display: none !important; }"
            ".block-container div[data-testid='stExpander'] { opacity: 0.92; }"
            ".iq-live-strip { border-color: rgba(255,192,72,0.35) !important; }"
            "</style>"
        )
        st.sidebar.caption("Board Mode on · calm presentation")
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
