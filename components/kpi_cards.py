"""Reusable KPI card grid — polished HTML cards, UI only."""
from __future__ import annotations

import html
from typing import Any

import streamlit as st

from config import settings
from utils.formatting import format_kpi_value


def render_kpi_cards(cards: list[dict[str, Any]], columns: int | None = None) -> None:
    """Render a responsive KPI strip. `columns` kept for API compatibility."""
    _ = columns or settings.KPI_COLUMNS
    pieces: list[str] = []
    for card in cards:
        label = html.escape(str(card["label"]))
        value = html.escape(format_kpi_value(card["value"], card.get("format", "int")))
        hint = card.get("help")
        hint_html = f'<div class="dss-kpi-hint">{html.escape(str(hint))}</div>' if hint else ""
        pieces.append(
            f'<div class="dss-kpi"><div class="dss-kpi-label">{label}</div>'
            f'<div class="dss-kpi-value">{value}</div>{hint_html}</div>'
        )
    # auto-fit grid via CSS — do not pin columns inline (breaks mobile)
    st.html(f'<div class="dss-kpi-grid">{"".join(pieces)}</div>')


def render_buyer_distribution(distribution: dict[str, int]) -> None:
    if not distribution:
        st.caption("No buyer distribution for current filters.")
        return
    total = sum(distribution.values()) or 1
    rows = sorted(distribution.items(), key=lambda x: -x[1])[:8]
    for name, count in rows:
        st.progress(min(count / total, 1.0), text=f"{name}: {count:,} ({count / total:.0%})")
