"""Buyer / Lead & Audience Demographics — AURA-Market."""
from __future__ import annotations

import sys
from pathlib import Path

import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from components.filters import render_global_filters
from components.kpi_cards import render_kpi_cards
from components.layout import page_hero, require_login, section_label
from services.buyer_service import build_buyer_insights
from services.data_loader import load_catalog
from utils.charts import PALETTE

st.set_page_config(page_title="Audience Demographics", page_icon="👥", layout="wide")
require_login()

page_hero(
    kicker="AURA-Market · Lead & Audience",
    title="Buyer & Audience Demographics",
    subtitle="Age profiles, native vs non-native origin, family type, first-time buyers, and conversion channels from booking Excels.",
    chips=[("Age bands", "ok"), ("Native / Outstation", "ok"), ("Family", ""), ("Channels", "")],
)

filters = render_global_filters("buyer")
insights = build_buyer_insights(filters)

section_label("Demand scorecard")
render_kpi_cards(
    [
        {"label": "Confirmed bookings", "value": insights.total_bookings, "format": "int"},
        {"label": "Channels", "value": len(insights.channel_mix), "format": "int"},
        {"label": "Age bands", "value": len(insights.age_profile), "format": "int"},
        {"label": "Origin segments", "value": len(insights.native_mix), "format": "int"},
    ]
)

if insights.total_bookings == 0:
    st.warning("No bookings for current filters.")
    st.stop()

section_label("Conversion channels & unit mix")
c1, c2 = st.columns(2)
with c1:
    st.plotly_chart(
        px.pie(insights.channel_mix.head(8), names="channel", values="count", title="Lead conversion channels", hole=0.45, color_discrete_sequence=PALETTE),
        width="stretch",
    )
with c2:
    st.plotly_chart(
        px.bar(insights.unit_mix.head(12), x="unit", y="count", title="Unit mix demand", color_discrete_sequence=PALETTE),
        width="stretch",
    )

section_label("Audience demographics")
a1, a2 = st.columns(2)
with a1:
    st.plotly_chart(
        px.bar(insights.age_profile, x="age_band", y="count", title="Age profile", color_discrete_sequence=PALETTE),
        width="stretch",
    )
    st.plotly_chart(
        px.pie(insights.native_mix, names="origin", values="count", title="Native vs non-native", hole=0.45, color_discrete_sequence=PALETTE),
        width="stretch",
    )
with a2:
    st.plotly_chart(
        px.bar(insights.family_mix, x="family_type", y="count", title="Family size proxy", color_discrete_sequence=PALETTE),
        width="stretch",
    )
    st.plotly_chart(
        px.bar(insights.first_time_mix, x="buyer_tenure", y="count", title="First-time vs other", color_discrete_sequence=PALETTE),
        width="stretch",
    )

section_label("Catchment — top postal codes")
st.dataframe(insights.top_pins, width="stretch", hide_index=True)

section_label("Lead funnel intelligence")
cat = load_catalog()
if cat.has("lead_insights"):
    st.caption("Lead Insights PDF was image-only — curated funnel grounded in booking channel mix.")
    st.dataframe(cat.get("lead_insights"), width="stretch", hide_index=True)

st.download_button(
    "Download channel mix CSV",
    insights.channel_mix.to_csv(index=False).encode("utf-8"),
    file_name="buyer_channel_mix.csv",
    mime="text/csv",
)
