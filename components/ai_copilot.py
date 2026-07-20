"""
Persistent AI Copilot — calm executive guide (not sci-fi HUD).
Rule guide only. No new ML models. No decorative motion theater.
"""
from __future__ import annotations

import html

import streamlit as st

from services.copilot_guide_service import SUGGESTED_PROMPTS, answer_copilot

CHAT_KEY = "iq_copilot_messages"
SOUND_KEY = "iq_sound_enabled"
OPEN_KEY = "iq_copilot_open"


def _active_module() -> str:
    return str(
        st.session_state.get("dss_nav_label_committed")
        or st.session_state.get("dss_nav_label")
        or "Executive Hub"
    )


def render_sound_pref() -> None:
    st.sidebar.toggle(
        "UI sounds (optional)",
        value=bool(st.session_state.get(SOUND_KEY, False)),
        key=SOUND_KEY,
        help="Off by default. Never continuous. Only a short cue when you opt in (e.g. report ready).",
    )


def maybe_play_success_chime(event: str = "ok") -> None:
    """One-shot optional cue — never ambient / looping."""
    if not st.session_state.get(SOUND_KEY):
        return
    freq = 880 if event == "ok" else 520
    st.html(
        f"""
        <script>
        (function() {{
          try {{
            const AC = window.AudioContext || window.webkitAudioContext;
            if (!AC) return;
            const ctx = new AC();
            const o = ctx.createOscillator();
            const g = ctx.createGain();
            o.type = 'sine';
            o.frequency.value = {freq};
            g.gain.value = 0.025;
            o.connect(g); g.connect(ctx.destination);
            o.start();
            g.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + 0.1);
            o.stop(ctx.currentTime + 0.11);
          }} catch (e) {{}}
        }})();
        </script>
        """
    )


def render_ai_copilot() -> None:
    """Sidebar control + quiet on-page panel when open. Enterprise tone."""
    module = _active_module()
    if OPEN_KEY not in st.session_state:
        st.session_state[OPEN_KEY] = False
    if CHAT_KEY not in st.session_state:
        st.session_state[CHAT_KEY] = []

    st.sidebar.markdown("---")
    st.sidebar.markdown("### AI Copilot")
    st.sidebar.caption(f"Page context · **{module}**")
    live = bool(st.session_state.get(OPEN_KEY))
    st.sidebar.caption("Open" if live else "Closed · answers questions about this page")
    if st.sidebar.button(
        "Close Copilot" if live else "Open Copilot",
        type="primary",
        width="stretch",
        key="iq_copilot_toggle",
    ):
        st.session_state[OPEN_KEY] = not live
        st.rerun()

    if not st.session_state.get(OPEN_KEY):
        return

    st.html(
        f"""
        <div class="iq-copilot-panel" role="complementary" aria-label="AI Copilot">
          <div class="iq-copilot-head">
            <div>
              <div class="iq-copilot-title">Executive Copilot</div>
              <div class="iq-copilot-sub">
                {html.escape(module)} · product guide · does not issue a second GO/HOLD
              </div>
            </div>
          </div>
        </div>
        """
    )

    persona = st.radio(
        "Explain for",
        ["Default", "CEO", "Sales Head", "Simple"],
        horizontal=True,
        key="iq_copilot_persona",
    )
    pick = st.selectbox(
        "Quick questions",
        ["(type below)"] + SUGGESTED_PROMPTS,
        key="iq_copilot_pick",
    )
    typed = st.text_input(
        "Ask the Copilot",
        placeholder="What should I do next? · Why is risk high?",
        key="iq_copilot_input",
    )

    def _compose(raw: str) -> str:
        q = (raw or "").strip() or "Summarize this page"
        if persona == "CEO":
            return f"Explain this for a CEO. {q}"
        if persona == "Sales Head":
            return f"Explain this for a Sales Head. {q}"
        if persona == "Simple":
            return f"Explain this simply. {q}"
        return q

    asked = False
    ask_raw = typed.strip() if typed.strip() else (pick if pick != "(type below)" else "")

    c1, c2, c3 = st.columns([2, 1, 1])
    with c1:
        if st.button("Ask Copilot", type="primary", width="stretch", key="iq_copilot_ask"):
            asked = True
    with c2:
        if st.button("Summarize page", width="stretch", key="iq_copilot_sum"):
            ask_raw = "Summarize this page"
            asked = True
    with c3:
        if st.button("Clear", width="stretch", key="iq_copilot_clear"):
            st.session_state[CHAT_KEY] = []
            st.rerun()

    if asked:
        ask = _compose(ask_raw)
        with st.spinner("Preparing a plain-language answer…"):
            reply = answer_copilot(ask, module=module)
        st.session_state[CHAT_KEY] = (
            st.session_state[CHAT_KEY]
            + [
                {"role": "user", "text": ask},
                {"role": "assistant", "text": reply},
            ]
        )[-12:]
        st.rerun()

    msgs = list(reversed(st.session_state.get(CHAT_KEY) or []))
    if not msgs:
        st.info(answer_copilot("", module=module)[:400] + "…")
    else:
        for m in msgs[:5]:
            if m["role"] == "user":
                st.markdown(f"**You:** {m['text']}")
            else:
                st.markdown(m["text"])
