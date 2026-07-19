"""AI Map Decision Support — dynamic proptech map-first UX."""
from __future__ import annotations

import sys
from pathlib import Path

import folium
import plotly.express as px
import streamlit as st
from streamlit_folium import st_folium

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from components.layout import decision_action, page_hero, require_login, section_label
from components.executive_sheet import render_executive_sheet
from components.states import data_honesty_banner, page_hub_label
from components.viz_studio import (
    generate_button,
    graphic_html,
    live_kpi_strip,
    render_dynamic_figure,
    scenario_bar,
)
from services.decision_brief_service import brief_from_map
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

st.set_page_config(page_title="Map Intelligence · RealEstateIQ", page_icon="🗺️", layout="wide")
require_login("Map Intelligence")

page_hub_label("Intelligence", "Map · Where to build")
data_honesty_banner(
    title="Map ML contract",
    lines=[
        "Zone suitability uses Random Forest on amenity/price features with illustrative pseudo-labels.",
        "Use for relative ranking in demo — not cadastral / PropStack-grade site selection.",
        "Metro stations are a curated overlay list, not a live GTFS feed.",
    ],
)

page_hero(
    kicker="Phase 2 · Location DSS",
    title="AI Map Decision Support System",
    subtitle="Map-first Bengaluru suitability — change filters & scenarios, regenerate graphics live (phone + desktop).",
    chips=[("25 zones", "ok"), ("Live regenerate", "ok"), ("Metro overlay", "")],
)

zones = scored_zones()
kpis = map_home_kpis(zones)

render_executive_sheet(
    brief_from_map(
        top_zone=str(kpis["ai_top_pick"]),
        high_risk=int(kpis["high_risk_zones"]),
        areas=int(kpis["areas_covered"]),
    ),
    key="map_eds",
)

live_kpi_strip(
    [
        {"label": "Areas", "display": str(kpis["areas_covered"]), "hint": "scored"},
        {"label": "Avg ₹/sqft", "display": f"{kpis['avg_price_psf']:,.0f}", "hint": "market"},
        {"label": "Top pick", "display": str(kpis["ai_top_pick"]), "hint": "AI"},
        {"label": "High-risk", "display": str(kpis["high_risk_zones"]), "hint": "score <50"},
    ]
)

t_home, t_map, t_ai, t_price, t_cmp, t_dmaic, t_heat = st.tabs(
    ["Home", "Interactive Map", "AI Analyzer", "Price Analytics", "Compare", "DMAIC / What-If", "Heatmap"]
)

with t_home:
    graphic_html("radar-orb.svg")
    decision_action(
        "Where to build / diligence next",
        [
            f"Prioritize land diligence in **{kpis['ai_top_pick']}**.",
            f"Defer high-risk zones ({kpis['high_risk_zones']}).",
            "Use Compare + What-If before acquisition terms.",
        ],
    )
    scene = scenario_bar("map_home_scene", "Home graphics", ["Top suitability", "Flood vs price", "Metro access"])
    generate_button("map_home", "Generate map-home graphics")

    def _map_home_fig():
        if scene == "Top suitability":
            d = zones.sort_values("suitability_score", ascending=False).head(10)
            fig = px.bar(d, x="suitability_score", y="zone", orientation="h", color="suitability_score",
                         color_continuous_scale=["#ff4b4b", "#f0b429", "#3dd68c"])
            return _style(fig, "Top construction-ready areas")
        if scene == "Flood vs price":
            fig = px.scatter(zones, x="flood_risk", y="avg_price_psf", color="suitability_score",
                             hover_name="zone", color_continuous_scale="Tealgrn")
            return _style(fig, "Flood risk vs price")
        fig = px.scatter(zones, x="metro_km", y="suitability_score", size="avg_price_psf",
                         color="flood_risk", hover_name="zone", color_discrete_sequence=PALETTE)
        return _style(fig, "Metro access vs suitability")

    render_dynamic_figure("map_home", _map_home_fig, height=400, scene=str(scene))
    top5 = zones.sort_values("suitability_score", ascending=False).head(5)
    st.dataframe(
        top5[["zone", "suitability_score", "avg_price_psf", "flood_risk", "metro_km", "price_trend_yoy_pct"]],
        width="stretch",
        hide_index=True,
    )

with t_map:
    section_label("Live map filters (mobile-friendly)")
    f1, f2 = st.columns(2)
    with f1:
        flood = st.multiselect("Flood risk", ["Low", "Medium", "High"], default=["Low", "Medium", "High"], key="map_flood")
    with f2:
        min_score = st.slider("Minimum AI score", 0, 100, 50, key="map_min_score")
    generate_button("map_folium", "Refresh interactive map")
    nonce = int(st.session_state.get("map_folium_nonce", 0))
    if st.session_state.pop("map_folium_flash", None):
        st.success(f"Map refreshed · pass #{nonce}")
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
    flood_key = "-".join(sorted(flood)) if flood else "none"
    st_folium(
        m,
        width=None,
        height=420,
        key=f"folium_{nonce}_{flood_key}_{min_score}_{len(view)}",
    )
    st.caption("Map height adapts via design tokens (≈280px phone · 340px tablet · 420px+ desktop).")
    st.dataframe(
        view[["zone", "suitability_score", "avg_price_psf", "flood_risk", "metro_km", "highway_km"]],
        width="stretch",
        hide_index=True,
    )

with t_ai:
    zone = st.selectbox("Analyse area", zones["zone"].tolist(), key="ai_zone")
    row = zones[zones["zone"] == zone].iloc[0]
    score = int(row["suitability_score"])
    badge = "GREEN" if score >= 75 else ("WATCH" if score >= 50 else "RISK")
    generate_button("map_ai", "Regenerate radar graphic")
    c1, c2 = st.columns([1, 1.1])
    with c1:
        st.markdown(f"### {badge} · {score}/100 — {row['suitability_label']}")
        st.write(f"**Price:** ₹{int(row['avg_price_psf']):,}/sqft · **Trend YoY:** {row['price_trend_yoy_pct']}%")
        for label, val, klass in explain_zone(row):
            st.write(f"- **{label}:** {val}")
    with c2:
        render_dynamic_figure(
            "map_ai",
            lambda: radar_chart(radar_values(row), f"{zone} radar"),
            height=400,
            scene=str(zone),
        )

with t_price:
    lens = scenario_bar("map_price_lens", "Price studio", ["Price Overview", "Trend Analysis", "Correlation"])
    generate_button("map_price", "Generate price graphics")

    def _price_fig():
        if lens == "Price Overview":
            return price_bar(zones)
        if lens == "Trend Analysis":
            fig = px.bar(
                zones.sort_values("price_trend_yoy_pct"),
                x="zone",
                y="price_trend_yoy_pct",
                color_discrete_sequence=PALETTE,
            )
            fig.update_layout(xaxis_tickangle=-35)
            return _style(fig, "YoY price trend %")
        return correlation_heatmap(zones)

    render_dynamic_figure("map_price", _price_fig, height=420, scene=str(lens))

with t_cmp:
    picks = st.multiselect(
        "Select 2–3 areas",
        zones["zone"].tolist(),
        default=["Bagaluru / KIADB", "Whitefield", "Electronic City"][:2],
    )
    generate_button("map_cmp", "Generate comparison radar")
    if len(picks) >= 2:
        cmp = zones[zones["zone"].isin(picks)].copy()
        best = cmp["suitability_score"].max()
        cmp["recommendation"] = cmp["suitability_score"].apply(lambda s: "Best Choice" if s == best else "Review")
        show_cols = [
            "zone",
            "suitability_score",
            "flood_risk",
            "avg_price_psf",
            "metro_km",
            "highway_km",
            "price_trend_yoy_pct",
            "recommendation",
        ]
        st.dataframe(cmp[show_cols], width="stretch", hide_index=True)
        a = cmp.iloc[0]
        b = cmp.iloc[1]
        render_dynamic_figure(
            "map_cmp",
            lambda: dual_radar(radar_values(a), radar_values(b), a["zone"], b["zone"]),
            height=400,
            scene="|".join(picks),
        )
    else:
        st.info("Pick at least two areas.")

with t_dmaic:
    section_label("Pareto — lower suitability concentration")
    generate_button("map_dmaic", "Regenerate DMAIC graphics")
    pareto = zones.sort_values("suitability_score").copy()
    pareto["risk_weight"] = 100 - pareto["suitability_score"]

    def _dmaic_fig():
        fig = px.bar(pareto.head(12), x="zone", y="risk_weight", color="flood_risk", color_discrete_sequence=PALETTE)
        fig.update_layout(xaxis_tickangle=-30)
        return _style(fig, "Lower suitability concentration")

    render_dynamic_figure("map_dmaic", _dmaic_fig, height=360, scene="pareto")
    st.plotly_chart(importance_chart(feature_importance(zones)), width="stretch")
    section_label("What-if scenario — live score drives graphic")
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
    baseline = float(zones["suitability_score"].median())
    st.metric("Live suitability prediction", f"{wi:.0f}/100", delta=f"{wi - baseline:+.0f} vs median zone")

    def _whatif_fig():
        fig = px.bar(
            x=["Median zone (baseline)", "Your what-if"],
            y=[baseline, wi],
            color=["Baseline", "What-if"],
            color_discrete_map={"Baseline": "#58a6ff", "What-if": "#3dd68c" if wi >= 70 else "#f0b429" if wi >= 50 else "#ff4b4b"},
        )
        return _style(fig, f"What-if suitability · {wi:.0f}/100")

    render_dynamic_figure(
        "map_whatif",
        _whatif_fig,
        height=320,
        scene=f"{metro}|{hwy}|{hosp}|{schools}|{malls}|{parks}|{flood_w}|{pop}|{price}|{trend}",
    )

with t_heat:
    generate_button("map_heat", "Refresh heatmap")
    render_dynamic_figure("map_heat", lambda: heatmap_scatter(zones), height=480, scene="heatmap")
    st.dataframe(
        zones.sort_values("suitability_score", ascending=False)[
            ["zone", "suitability_score", "avg_price_psf", "price_trend_yoy_pct", "flood_risk", "metro_km", "suitability_label"]
        ],
        width="stretch",
        hide_index=True,
    )
