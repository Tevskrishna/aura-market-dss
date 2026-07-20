"""
Shared navigation config — kept separate from layout.py to avoid circular imports
(touch_nav ↔ layout) that raise ImportError: cannot import name MODULE_NAV.
"""
from __future__ import annotations

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
    ("Decision Explanation", "pages/8_AI_Recommendations.py"),
    ("SPC Control", "pages/9_SPC_Control_Chart.py"),
    ("Map Intelligence", "pages/10_Map_Decision_Support.py"),
    ("Reports", "pages/11_Executive_Reports.py"),
    ("Demand Forecast", "pages/12_Forecasting.py"),
]

# Sidebar IA — ≤7 sections, same 13 routes (CEO Morning Loop)
NAV_SECTIONS: list[tuple[str, list[str]]] = [
    ("Executive Decision", ["Executive Hub", "Decision Explanation", "Reports"]),
    ("Market & Land", ["Market Intelligence", "Competition & Land", "Map Intelligence"]),
    ("Customers & Growth", ["Buyer Intelligence", "Marketing Intelligence"]),
    ("Simulate", ["Digital Twin", "Demand Forecast"]),
    ("Quality Evidence", ["DMAIC Quality", "Project Deep Dive", "SPC Control"]),
]
