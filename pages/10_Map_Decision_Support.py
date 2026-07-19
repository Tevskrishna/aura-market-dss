"""AI Map Decision Support — Phase-2 (tabs cover original Map DSS pages)."""
from __future__ import annotations

import sys
from pathlib import Path

import folium
import pandas as pd
import plotly.express as px
import streamlit as st
from streamlit_folium import st_folium

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from components.kpi_cards import render_kpi_cards
from components.layout import decision_action, page_hero, require_login, section_label
from services.map_service import (
    METRO_STATIONS,
    explain_zone,
    feature_importance,
    map_home_kpis,
    radar_values,
    scored_zones,
    what_if_score,
)
from utils.map_charts import (
    correlation_heatmap,
    dual_radar,
    heatmap_scatter,
    importance_chart,
    price_bar,
    radar_chart,
)
from utils.charts import PALETTE, _style

st.set_page_config(page_title="Map Decision Support", page_icon="🗺️", layout="wide")
require_login()

page_hero(
    kicker="Phase 2 · Location DSS",
    title="AI Map Decision Support System",
    subtitle="Score 25 Bengaluru zones for construction suitability — map, radar, price analytics, compare, what-if.",
    chips=[("25 zones", "ok"), ("ML suitability", "ok"), ("Metro overlay", "")],
)

zones = scored_zones()
kpis = map_home_kpis(zones)

t_home, t_map, t_ai, t_price, t_cmp, t_dmaic, t_heat = st.tabs(
    ["Home", "Interactive Map", "AI Analyzer", "Price Analytics", "Compare", "DMAIC / What-If", "Heatmap"]
)

with t_home:
    section_label("Location scorecard")
    render_kpi_cards(
        [
            {"label": "Areas Covered", "value": kpis["areas_covered"], "format": "int"},
            {"label": "Avg Price/sqft", "value": kpis["avg_price_psf"], "format": "float"},
            {"label": "High-Risk Zones", "value": kpis["high_risk_zones"], "format": "int"},
        ],
        columns=3,
    )
    st.info(f"Highest growth area: **{kpis['highest_growth_area']}** · AI top-pick: **{kpis['ai_top_pick']}**")
    decision_action(
        "Where to build / diligence next",
        [
            f"Prioritize land and construction diligence in **{kpis['ai_top_pick']}** (AI top-pick).",
            f"Defer or redesign zones counted in high-risk ({kpis['high_risk_zones']}) — flood or score <50.",
            "Use Compare + What-If tabs before committing acquisition terms.",
        ],
    )
    top5 = zones.sort_values("suitability_score", ascending=False).head(5)
    st.dataframe(top5[["zone", "suitability_score", "avg_price_psf", "flood_risk", "metro_km", "price_trend_yoy_pct"]], width="stretch", hide_index=True)
    st.caption("ML inputs: price, trend, metro, highway, hospitals, schools, malls, parks, flood, AQI, population growth")

with t_map:
    flood = st.sidebar.multiselect("Flood risk", ["Low", "Medium", "High"], default=["Low", "Medium", "High"])
    min_score = st.sidebar.slider("Minimum AI score", 0, 100, 50)
    view = zones[(zones["flood_risk"].isin(flood)) & (zones["suitability_score"] >= min_score)]
    m = folium.Map(location=[12.98, 77.60], zoom_start=10, tiles="CartoDB dark_matter")
    for _, z in view.iterrows():
        color = "#3dd68c" if z["suitability_score"] >= 75 else ("#f0b429" if z["suitability_score"] >= 50 else "#ff4b4b")
        folium.CircleMarker(
            [z["lat"], z["lon"]],
            radius=9,
            color=color,
            fill=True,
            fill_opacity=0.85,
            popup=folium.Popup(
                f"<b>{z['zone']}</b><br>Score {z['suitability_score']}<br>₹{int(z['avg_price_psf']):,}/sqft"
                f"<br>Road {z['highway_km']} km · Flood {z['flood_risk']}<br>Metro {z['metro_km']} km",
                max_width=260,
            ),
        ).add_to(m)
    line_colors = {"Purple": "#7c3aed", "Green": "#16a34a", "Purple/Green": "#2563eb", "Yellow planned": "#ca8a04"}
    for _, s in METRO_STATIONS.iterrows():
        folium.CircleMarker(
            [s["lat"], s["lon"]],
            radius=5,
            color=line_colors.get(s["line"], "#334155"),
            fill=True,
            popup=f"Metro: {s['station']} ({s['line']})",
        ).add_to(m)
    st_folium(m, width=None, height=380)
    st.dataframe(view[["zone", "suitability_score", "avg_price_psf", "flood_risk", "metro_km", "highway_km"]], width="stretch", hide_index=True)

with t_ai:
    zone = st.selectbox("Analyse area", zones["zone"].tolist(), key="ai_zone")
    row = zones[zones["zone"] == zone].iloc[0]
    score = int(row["suitability_score"])
    badge = "🟢" if score >= 75 else ("🟡" if score >= 50 else "🔴")
    c1, c2 = st.columns([1, 1.1])
    with c1:
        st.markdown(f"### {badge} {score}/100 — {row['suitability_label']}")
        st.write(f"**Price:** ₹{int(row['avg_price_psf']):,}/sqft · **Trend YoY:** {row['price_trend_yoy_pct']}%")
        for label, val, klass in explain_zone(row):
            st.write(f"- **{label}:** {val}")
    with c2:
        st.plotly_chart(radar_chart(radar_values(row), f"{zone} radar"), width="stretch")

with t_price:
    p1, p2, p3 = st.tabs(["Price Overview", "Trend Analysis", "Correlation"])
    with p1:
        st.plotly_chart(price_bar(zones), width="stretch")
    with p2:
        fig = px.scatter(zones, x="flood_risk", y="avg_price_psf", color="suitability_score", hover_name="zone", color_continuous_scale="Tealgrn")
        st.plotly_chart(_style(fig, "Flood risk vs price"), width="stretch")
        fig2 = px.bar(zones.sort_values("price_trend_yoy_pct"), x="zone", y="price_trend_yoy_pct", color_discrete_sequence=PALETTE)
        fig2.update_layout(xaxis_tickangle=-35)
        st.plotly_chart(_style(fig2, "YoY price trend %"), width="stretch")
    with p3:
        st.plotly_chart(correlation_heatmap(zones), width="stretch")

with t_cmp:
    picks = st.multiselect("Select 2–3 areas", zones["zone"].tolist(), default=["Bagaluru / KIADB", "Whitefield", "Electronic City"][:2])
    if len(picks) >= 2:
        cmp = zones[zones["zone"].isin(picks)].copy()
        best = cmp["suitability_score"].max()
        cmp["recommendation"] = cmp["suitability_score"].apply(lambda s: "⭐ Best Choice" if s == best else "Review")
        show_cols = ["zone", "suitability_score", "flood_risk", "avg_price_psf", "metro_km", "highway_km", "price_trend_yoy_pct", "recommendation"]
        st.dataframe(cmp[show_cols].set_index("zone").T, width="stretch")
        a = cmp.iloc[0]
        b = cmp.iloc[1]
        st.plotly_chart(dual_radar(radar_values(a), radar_values(b), a["zone"], b["zone"]), width="stretch")
    else:
        st.info("Pick at least two areas.")

with t_dmaic:
    section_label("Pareto — high-risk / lower-score inventory proxy")
    pareto = zones.sort_values("suitability_score").copy()
    pareto["risk_weight"] = 100 - pareto["suitability_score"]
    fig = px.bar(pareto.head(12), x="zone", y="risk_weight", color="flood_risk", color_discrete_sequence=PALETTE)
    fig.update_layout(xaxis_tickangle=-30)
    st.plotly_chart(_style(fig, "Lower suitability concentration"), width="stretch")
    st.plotly_chart(importance_chart(feature_importance(zones)), width="stretch")
    section_label("What-if scenario")
    metro = st.slider("Metro distance km", 0.2, 10.0, 2.0)
    hwy = st.slider("Highway km", 0.2, 12.0, 3.0)
    hosp = st.slider("Hospitals", 0, 20, 5)
    schools = st.slider("Schools", 0, 25, 8)
    malls = st.slider("Malls", 0, 15, 3)
    parks = st.slider("Parks", 0, 15, 4)
    flood_w = st.selectbox("Flood risk", ["Low", "Medium", "High"])
    pop = st.slider("Population growth index", 40, 100, 75)
    price = st.slider("Price ₹/sqft", 5000, 18000, 9000, 100)
    trend = st.slider("YoY trend %", 0.0, 20.0, 8.0)
    wi = what_if_score(metro, hwy, hosp, schools, malls, parks, flood_w, pop, price, trend)
    st.metric("Live suitability prediction", f"{wi:.0f}/100")

with t_heat:
    st.plotly_chart(heatmap_scatter(zones), width="stretch")
    st.dataframe(
        zones.sort_values("suitability_score", ascending=False)[
            ["zone", "suitability_score", "avg_price_psf", "price_trend_yoy_pct", "flood_risk", "metro_km", "suitability_label"]
        ],
        width="stretch",
        hide_index=True,
    )
