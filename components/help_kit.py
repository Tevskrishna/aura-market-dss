"""
Contextual help kit — plain-language what / why / how / action.
Reusable across KPIs, charts, and recommendations. UI-only.
"""
from __future__ import annotations

import html

import streamlit as st


def help_tip(
    label: str,
    *,
    what: str,
    why: str,
    how: str = "",
    action: str = "",
    key: str | None = None,
) -> None:
    """Compact info control — expander keeps layout calm."""
    k = key or f"help_{abs(hash(label)) % 10_000_000}"
    with st.expander(f"ⓘ What is {label}?", expanded=False):
        st.markdown(f"**What it is:** {what}")
        st.markdown(f"**Why it matters:** {why}")
        if how:
            st.markdown(f"**How to read it (high level):** {how}")
        if action:
            st.markdown(f"**Business action:** {action}")


def help_caption(text: str) -> None:
    """One-line purpose under a section — reduces ‘why am I here?’"""
    st.caption(text)


def purpose_banner(question: str, after_click: str) -> None:
    """Every screen states the business question and what Continue does."""
    st.html(
        f'<div class="iq-purpose" role="note">'
        f'<span class="iq-purpose-q">{html.escape(question)}</span>'
        f'<span class="iq-purpose-next">{html.escape(after_click)}</span>'
        f"</div>"
    )


# Canonical help copy for Hub / shared metrics (no calculation changes)
HUB_HELP = {
    "threat_score": {
        "what": "A 0–100 Launch Threat Score fusing competition pressure, inventory, twin ₹ Cr exposure, and margin viability.",
        "why": "Gives leadership one number instead of debating five conflicting reports.",
        "how": "Higher = more launch risk. Colour bands map to GO / HOLD / NO-GO on the Hub only.",
        "action": "If high, open Competition and Digital Twin before printing brochures.",
    },
    "blind_spot": {
        "what": "Estimated ₹ Cr revenue at risk if a rival launches and you do not intervene.",
        "why": "Turns a competition blind spot into money leadership understands.",
        "how": "Directional twin output — use for IC discussion, not as audited P&L.",
        "action": "Compare to Recovery ₹ Cr; if loss >> recovery, lean HOLD.",
    },
    "recovery": {
        "what": "Estimated ₹ Cr you can claw back with the intervene package (cut / subvention / timing).",
        "why": "Shows whether action is worth the commercial cost.",
        "how": "Same twin engine as Hub and Digital Twin — illustrative.",
        "action": "Lock intervene month and cut % before marketing spend scales.",
    },
}
