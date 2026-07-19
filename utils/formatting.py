"""Display formatters — no Plotly / Streamlit business logic."""
from __future__ import annotations


def format_kpi_value(value, fmt: str) -> str:
    if value is None:
        return "—"
    if fmt == "int":
        return f"{int(value):,}"
    if fmt == "pct":
        return f"{float(value):.1f}%"
    if fmt == "cr":
        return f"₹ {float(value):,.2f} Cr"
    if fmt == "float":
        return f"{float(value):,.2f}"
    return str(value)
