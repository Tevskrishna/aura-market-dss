"""
Live session presence — honest realtime (session decision age), not fake market feeds.
"""
from __future__ import annotations

import html

import streamlit as st

from services.decision_context import format_relative_age, get_decision_context


def render_live_presence() -> None:
    """Sticky strip: open project + freshness. Updates on every interaction."""
    ctx = get_decision_context()
    if not ctx:
        st.html(
            '<div class="iq-live-presence" role="status">'
            '<span class="iq-live-presence-dot" style="background:#8a9bb0"></span>'
            "<span><strong>Live session</strong> · set project on Executive Hub — "
            "decision context will follow you across modules</span>"
            "</div>"
        )
        return
    project = html.escape(str(ctx.get("project") or "—"))
    verdict = html.escape(str(ctx.get("verdict") or "—"))
    price = float(ctx.get("my_price_psf") or 0)
    age = html.escape(format_relative_age(ctx.get("updated_at")))
    st.html(
        f'<div class="iq-live-presence" role="status" aria-live="polite">'
        f'<span class="iq-live-presence-dot" aria-hidden="true"></span>'
        f"<span><strong>Live decision</strong> · {project} · ₹{price:,.0f}/sqft · "
        f"Hub {verdict} · {age}</span>"
        f"</div>"
    )


def render_mobile_dock() -> None:
    """Phone footer: where you are + how to open menu / continue."""
    module = str(
        st.session_state.get("dss_nav_label_committed")
        or st.session_state.get("dss_nav_label")
        or "Executive Hub"
    )
    st.html(
        f'<div class="iq-mobile-dock" role="contentinfo">'
        f"<strong>{html.escape(module)}</strong>"
        f" · Menu (☰ top-left) · Continue buttons above · "
        f"Copilot in sidebar"
        f"</div>"
    )
