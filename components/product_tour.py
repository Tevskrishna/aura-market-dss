"""
Product orientation tour — welcome, purpose, journey, time, skip/replay.
"""
from __future__ import annotations

import html

import streamlit as st

TOUR_DONE_KEY = "iq_tour_done"
TOUR_STEP_KEY = "iq_tour_step"
TOUR_FORCE_KEY = "iq_tour_force"

TOUR_STEPS: list[dict[str, str]] = [
    {
        "title": "Welcome to RealEstateIQ",
        "body": (
            "An intelligent executive assistant for developer launch decisions. "
            "Not twelve dashboards — one guided Decision Support System."
        ),
        "outcome": "You will always know where you are and what to do next.",
    },
    {
        "title": "The problem we solve",
        "body": (
            "Today launch calls pull Sales, CRM, Marketing, Finance, Competition, Land, "
            "Excel, and meetings. Reports conflict. Risks slip. There is no single answer."
        ),
        "outcome": "RealEstateIQ answers: Should we launch this project at this price?",
    },
    {
        "title": "Where you start",
        "body": (
            "Executive Hub — select the project once, set ₹/sqft, read the only final call: "
            "GO / HOLD / NO-GO. Everything else is evidence."
        ),
        "outcome": "≈ 30 seconds to know project status.",
    },
    {
        "title": "The journey (~10 minutes)",
        "body": (
            "Continue through Market → Competition → Buyer → Marketing → DMAIC → Project → "
            "Twin → Decision Explanation → SPC → Reports. Open the floating AI Copilot anytime."
        ),
        "outcome": "≈ 3–5 minutes to understand why; ≈ 10 minutes to a board pack.",
    },
    {
        "title": "You are ready",
        "body": (
            "Skip anytime. Replay from the sidebar. Sounds stay off unless you enable them. "
            "Press Start to begin on the Executive Hub."
        ),
        "outcome": "Clear path. One decision. Board-ready close.",
    },
]


def tour_should_show() -> bool:
    if st.session_state.get(TOUR_FORCE_KEY):
        return True
    return not bool(st.session_state.get(TOUR_DONE_KEY))


def start_tour_replay() -> None:
    st.session_state[TOUR_FORCE_KEY] = True
    st.session_state[TOUR_STEP_KEY] = 0


def complete_tour() -> None:
    st.session_state[TOUR_DONE_KEY] = True
    st.session_state[TOUR_FORCE_KEY] = False
    st.session_state[TOUR_STEP_KEY] = 0


def skip_tour() -> None:
    complete_tour()


def render_product_tour() -> None:
    if not tour_should_show():
        return

    step = int(st.session_state.get(TOUR_STEP_KEY, 0))
    step = max(0, min(step, len(TOUR_STEPS) - 1))
    item = TOUR_STEPS[step]
    total = len(TOUR_STEPS)

    st.html(
        f"""
        <div class="iq-tour" role="dialog" aria-label="Product tour">
          <div class="iq-tour-kicker">Welcome · Step {step + 1} of {total} · ~2 minutes · Skip anytime</div>
          <h2 class="iq-tour-title">{html.escape(item["title"])}</h2>
          <p class="iq-tour-body">{html.escape(item["body"])}</p>
          <div class="iq-tour-outcome"><strong>Outcome:</strong> {html.escape(item["outcome"])}</div>
          <div class="iq-tour-track"><div class="iq-tour-fill" style="width:{(step + 1) / total * 100:.0f}%"></div></div>
        </div>
        """
    )

    c1, c2, c3 = st.columns([1, 1, 1])
    with c1:
        if st.button("Skip tour", width="stretch", key="iq_tour_skip"):
            skip_tour()
            st.rerun()
    with c2:
        if step > 0 and st.button("← Back", width="stretch", key="iq_tour_back"):
            st.session_state[TOUR_STEP_KEY] = step - 1
            st.rerun()
    with c3:
        if step < total - 1:
            if st.button("Next →", type="primary", width="stretch", key="iq_tour_next"):
                st.session_state[TOUR_STEP_KEY] = step + 1
                st.rerun()
        else:
            if st.button("Start on Executive Hub", type="primary", width="stretch", key="iq_tour_done"):
                complete_tour()
                st.rerun()
