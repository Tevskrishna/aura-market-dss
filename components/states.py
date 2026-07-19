"""Reusable empty / error / loading / honesty UI states — P0 design system."""
from __future__ import annotations

import html

import streamlit as st


def data_honesty_banner(
    *,
    title: str = "Data contract",
    lines: list[str] | None = None,
    compact: bool = True,
) -> None:
    """Enterprise trust label — seed vs measured data (P0-1).

    compact=True (default): collapsed expander so it never steals the 10s decision.
    """
    lines = lines or [
        "Competition RERA / upcoming / UC / land layers use curated seed CSVs until live adapters are connected.",
        "Bookings + SMC spends are from provided project Excels (measured).",
        "Map suitability ML uses illustrative pseudo-labels — not cadastral PropStack truth.",
    ]
    items = "".join(f"<li>{html.escape(x)}</li>" for x in lines)
    body = (
        f'<div class="iq-honesty" role="note">'
        f'<div class="iq-honesty-kicker">{html.escape(title)}</div>'
        f"<ul>{items}</ul></div>"
    )
    if compact:
        with st.expander(f"{title} · measured vs seed", expanded=False):
            st.html(body)
    else:
        st.html(body)


def empty_state(title: str, detail: str = "", action_hint: str = "") -> None:
    hint = f'<p class="iq-state-hint">{html.escape(action_hint)}</p>' if action_hint else ""
    detail_html = f"<p>{html.escape(detail)}</p>" if detail else ""
    st.html(
        f'<div class="iq-state iq-empty">'
        f"<h4>{html.escape(title)}</h4>{detail_html}{hint}</div>"
    )


def error_state(title: str, detail: str = "") -> None:
    detail_html = f"<p>{html.escape(detail)}</p>" if detail else ""
    st.html(
        f'<div class="iq-state iq-error" role="alert">'
        f"<h4>{html.escape(title)}</h4>{detail_html}</div>"
    )


def loading_state(label: str = "Loading…") -> None:
    st.html(
        f'<div class="iq-state iq-loading"><div class="iq-spinner"></div>'
        f"<span>{html.escape(label)}</span></div>"
    )


def page_hub_label(hub: str, title: str) -> None:
    """Consistent hub eyebrow for nested IA (P0-2)."""
    st.html(
        f'<div class="iq-hub-label"><span>{html.escape(hub)}</span>'
        f"<strong>{html.escape(title)}</strong></div>"
    )
