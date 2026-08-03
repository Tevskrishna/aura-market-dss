"""Market Intelligence — Stitch Bagaluru snapshot + PropStack series."""
from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from components.filters import render_global_filters
from components.layout import require_login, section_label
from components.states import empty_state, error_state
from components.stitch_ui import (
    end_stitch_page,
    render_bagaluru_snapshot,
    render_portfolio_table,
    render_topbar,
)
from components.touch_nav import navigate_to
from components.viz_studio import render_dynamic_figure, scenario_bar
from services.data_loader import load_catalog
from services.market_service import (
    build_market_bundle,
    get_validation_report,
    propstack_absorption_bands,
    propstack_inventory,
    propstack_new_launches,
    propstack_price_trend,
    propstack_summary_row,
)
from services.sigma_service import market_kpis as sigma_kpis
from utils.charts import (
    absorption_price_band_chart,
    inventory_trend_chart,
    new_launch_pulse_chart,
    weighted_price_trend_chart,
)
from utils.dmaic_charts import absorption_band_chart, price_absorption_bubble

st.set_page_config(page_title="Market Intelligence · RealEstateIQ", page_icon="📊", layout="wide")
require_login("Market Intelligence")

report = get_validation_report()
if not report or not report.ready_for_market_overview:
    error_state(
        "Core datasets failed validation",
        "Market overview cannot load until catalog validation passes.",
    )
    st.stop()

render_topbar()

st.html(
    """
    <div class="st-mkt-head">
      <div>
        <h2 class="st-page-title">Market Intelligence Overview</h2>
        <p class="st-page-sub">Institutional data streams for Bagaluru residential · PropStack Dec 2022 – Nov 2025.</p>
      </div>
      <p class="st-mkt-asof">Data current · PropStack Nov 2025</p>
    </div>
    """
)

catalog = load_catalog()
filters = render_global_filters("market")
bundle = build_market_bundle(filters, catalog)
sk = sigma_kpis(bundle.projects)
projects = bundle.projects

if projects.empty:
    empty_state(
        "No projects in filtered market view",
        "Widen filters or reset to all builders / projects.",
        "Clear filters in the control strip above.",
    )
    st.stop()

ps = propstack_summary_row(catalog)
render_bagaluru_snapshot(ps)

inv = propstack_inventory(catalog)
price = propstack_price_trend(catalog)
launches = propstack_new_launches(catalog)
bands = propstack_absorption_bands(catalog)

chart_col, thesis_col = st.columns([2, 1], gap="large")
with chart_col:
    st.html(
        """
        <div class="st-card-head">
          <div>
            <h3 class="st-section-title" style="margin:0;">Weighted Price Trend</h3>
            <p class="st-card-sub">Historical quarterly pricing variance per sq. ft. (institutional grade)</p>
          </div>
          <div class="st-legend">
            <span><i class="c-terra"></i> Primary market</span>
            <span><i class="c-ink"></i> Secondary / available</span>
          </div>
        </div>
        """
    )
    ps_lens = scenario_bar(
        "mkt_propstack_lens",
        "Series lens",
        ["Price trend", "Inventory", "New launches", "Price bands", "Project absorption"],
    )

    def _ps_fig():
        if ps_lens == "Inventory":
            return inventory_trend_chart(inv)
        if ps_lens == "New launches":
            return new_launch_pulse_chart(launches)
        if ps_lens == "Price bands":
            return absorption_price_band_chart(bands)
        if ps_lens == "Project absorption":
            return absorption_band_chart(projects)
        return weighted_price_trend_chart(price)

    st.html('<div class="st-chart-card">')
    render_dynamic_figure("mkt_propstack", _ps_fig, height=380, scene=f"ps|{ps_lens}|{len(projects)}")
    st.html("</div>")

with thesis_col:
    abs_pct = float(ps["absorption_pct"]) if ps else float(sk.get("absorption_pct", 0))
    at_risk = int(sk.get("at_risk_projects", 0))
    risk_q = "L-04 (Low)" if at_risk <= 2 else ("M-06 (Watch)" if at_risk <= 5 else "H-08 (Elevated)")
    liq = min(0.99, abs_pct / 100)
    st.html(
        f"""
        <div class="st-thesis">
          <div class="st-thesis-kicker">Investment thesis</div>
          <h3>North-East corridor outperformance</h3>
          <p>
            PropStack Bagaluru shows <strong>{abs_pct:.0f}%</strong> absorption across launched supply,
            with IT-corridor demand and ring-road connectivity supporting mid-premium liquidity.
            Use this page as Hub evidence — not a second launch call.
          </p>
          <div class="st-thesis-rows">
            <div><span>Risk quotient</span><strong>{risk_q}</strong></div>
            <div><span>Liquidity index</span><strong>{liq:.2f} {"High" if liq >= 0.75 else "Moderate"}</strong></div>
            <div><span>At-risk projects</span><strong>{at_risk}</strong></div>
            <div><span>Unsold pool</span><strong>{int(sk.get("units_unsold", 0)):,}</strong></div>
          </div>
        </div>
        """
    )

st.html(
    """
    <div class="st-card-head" style="margin-top:1.5rem;">
      <h3 class="st-section-title" style="margin:0;">Micro-Market Portfolio Analysis</h3>
    </div>
    """
)
focus_c1, focus_c2, focus_c3 = st.columns(3)
with focus_c1:
    if st.button("Focus at-risk", type="primary", width="stretch", key="mkt_focus_risk"):
        st.session_state["mkt_focus"] = "at_risk"
with focus_c2:
    if st.button("Show sold-out", width="stretch", key="mkt_focus_sold"):
        st.session_state["mkt_focus"] = "sold_out"
with focus_c3:
    if st.button("Reset view", width="stretch", key="mkt_focus_reset"):
        st.session_state["mkt_focus"] = "all"

focus = st.session_state.get("mkt_focus", "all")
if focus == "at_risk":
    view = projects[projects["absorption_pct"] < 70].sort_values("absorption_pct")
elif focus == "sold_out":
    view = projects[projects["absorption_pct"] >= 95].sort_values("absorption_pct", ascending=False)
else:
    view = projects.sort_values("absorption_pct", ascending=False)

render_portfolio_table(view)

with st.expander("Price vs absorption bubble · CSV export", expanded=False):
    render_dynamic_figure(
        "mkt_bubble",
        lambda: price_absorption_bubble(view if not view.empty else projects),
        height=360,
        scene=f"bubble|{focus}|{len(view)}",
    )
    cols = [
        c
        for c in ["developer", "project", "price_psf", "absorption_pct", "total_units", "units_unsold", "status"]
        if c in view.columns
    ]
    st.download_button(
        "Download portfolio CSV",
        view[cols].to_csv(index=False).encode("utf-8"),
        file_name="bagaluru_portfolio.csv",
        mime="text/csv",
        width="stretch",
    )

nav1, nav2, nav3 = st.columns(3)
with nav1:
    if st.button("→ Competition & Land", width="stretch", key="mkt_go_comp"):
        navigate_to("Competition & Land", "pages/2_Competition_Intelligence.py")
with nav2:
    if st.button("→ Scenario Engine", width="stretch", key="mkt_go_twin"):
        navigate_to("Scenario Engine", "pages/7_Digital_Twin.py")
with nav3:
    if st.button("→ Decision Explanation", width="stretch", key="mkt_go_recs"):
        navigate_to("Decision Explanation", "pages/8_AI_Recommendations.py")

end_stitch_page("Market Intelligence")
