from pathlib import Path

root = Path(__file__).resolve().parents[1]
mapping = {
    "app.py": "Executive Hub",
    "pages/2_Competition_Intelligence.py": "Competition & Land",
    "pages/3_Buyer_Analytics.py": "Buyer Intelligence",
    "pages/4_Marketing_Intelligence.py": "Marketing Intelligence",
    "pages/5_DMAIC_Workspace.py": "DMAIC Quality",
    "pages/6_Builder_Deep_Dive.py": "Project Deep Dive",
    "pages/7_Digital_Twin.py": "Scenario Engine",
    "pages/8_AI_Recommendations.py": "AI Recommendations",
    "pages/9_SPC_Control_Chart.py": "SPC Control",
    "pages/10_Map_Decision_Support.py": "Map Intelligence",
    "pages/11_Executive_Reports.py": "Reports",
    "pages/12_Forecasting.py": "Demand Forecast",
}
for rel, label in mapping.items():
    p = root / rel
    text = p.read_text(encoding="utf-8")
    if 'require_login()' in text:
        text = text.replace("require_login()", f'require_login("{label}")', 1)
        p.write_text(text, encoding="utf-8")
        print("updated", rel)
    elif f'require_login("{label}")' in text:
        print("already", rel)
    else:
        print("missing require_login", rel)
