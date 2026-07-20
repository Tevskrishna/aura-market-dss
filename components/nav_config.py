"""
Shared navigation config — kept separate from layout.py to avoid circular imports.
"""
from __future__ import annotations

# Full catalog (Quality Lab when IC Demo Mode is off)
MODULE_NAV: list[tuple[str, str]] = [
    ("Executive Hub", "app.py"),
    ("Market Intelligence", "pages/1_Market_Overview.py"),
    ("Competition & Land", "pages/2_Competition_Intelligence.py"),
    ("Buyer Intelligence", "pages/3_Buyer_Analytics.py"),
    ("Marketing Intelligence", "pages/4_Marketing_Intelligence.py"),
    ("DMAIC Quality", "pages/5_DMAIC_Workspace.py"),
    ("Project Deep Dive", "pages/6_Builder_Deep_Dive.py"),
    ("Scenario Engine", "pages/7_Digital_Twin.py"),
    ("Decision Explanation", "pages/8_AI_Recommendations.py"),
    ("SPC Control", "pages/9_SPC_Control_Chart.py"),
    ("Map Intelligence", "pages/10_Map_Decision_Support.py"),
    ("Reports", "pages/11_Executive_Reports.py"),
    ("Demand Forecast", "pages/12_Forecasting.py"),
]

# Enterprise IC demo spine — ~6 surfaces (highest-ROI cut from ENTERPRISE_REVIEW)
IC_DEMO_LABELS: frozenset[str] = frozenset(
    {
        "Executive Hub",
        "Market Intelligence",
        "Competition & Land",
        "Scenario Engine",
        "Decision Explanation",
        "Reports",
    }
)

NAV_SECTIONS_FULL: list[tuple[str, list[str]]] = [
    ("Executive Decision", ["Executive Hub", "Decision Explanation", "Reports"]),
    ("Market & Land", ["Market Intelligence", "Competition & Land", "Map Intelligence"]),
    ("Customers & Growth", ["Buyer Intelligence", "Marketing Intelligence"]),
    ("Simulate", ["Scenario Engine", "Demand Forecast"]),
    ("Quality Lab", ["DMAIC Quality", "Project Deep Dive", "SPC Control"]),
]

NAV_SECTIONS_IC: list[tuple[str, list[str]]] = [
    ("IC Decision Path", [
        "Executive Hub",
        "Market Intelligence",
        "Competition & Land",
        "Scenario Engine",
        "Decision Explanation",
        "Reports",
    ]),
]

# Backward-compatible default (overridden at runtime by ic_demo_mode)
NAV_SECTIONS = NAV_SECTIONS_IC


def path_by_label() -> dict[str, str]:
    return dict(MODULE_NAV)


def modules_for_mode(*, ic_demo: bool) -> list[tuple[str, str]]:
    if ic_demo:
        return [m for m in MODULE_NAV if m[0] in IC_DEMO_LABELS]
    return list(MODULE_NAV)


def sections_for_mode(*, ic_demo: bool) -> list[tuple[str, list[str]]]:
    return NAV_SECTIONS_IC if ic_demo else NAV_SECTIONS_FULL


# Land diligence display — never reuse Hub GO/HOLD/NO-GO words
LAND_DILIGENCE_LABEL = {
    "BUY": "Proceed",
    "HOLD": "Caution",
    "PASS": "Walk",
}
