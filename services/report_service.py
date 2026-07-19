"""
Executive report generation — submission-ready summaries from shared services.
"""
from __future__ import annotations

from datetime import date

import pandas as pd

from config import settings
from models.market import FilterState
from services.adapters import get_adapter
from services.competition_service import build_competition_snapshot
from services.dmaic_service import build_dmaic_snapshot
from services.map_service import map_home_kpis, scored_zones
from services.market_service import build_market_bundle
from services.sigma_service import market_kpis


def default_filters() -> FilterState:
    return FilterState(
        builder=settings.ALL_BUILDERS_LABEL,
        project=settings.ALL_PROJECTS_LABEL,
        date_start=date(2022, 12, 1),
        date_end=date(2025, 11, 30),
        quarter=settings.ALL_QUARTERS_LABEL,
    )


def build_executive_markdown(filters: FilterState | None = None) -> str:
    filters = filters or default_filters()
    bundle = build_market_bundle(filters)
    sk = market_kpis(bundle.projects)
    dmaic = build_dmaic_snapshot(filters)
    comp = build_competition_snapshot()
    zones = scored_zones()
    mk = map_home_kpis(zones)
    adapter = get_adapter().meta()

    lines = [
        f"# Executive Decision Brief — {settings.COMPANY_NAME}",
        f"",
        f"**Generated:** {date.today().isoformat()}  ",
        f"**Micro-market:** {settings.MICRO_MARKET_DEFAULT}  ",
        f"**Data mode:** {adapter.mode} — {adapter.description}",
        f"",
        "## 1. Situation (DEFINE)",
        f"",
        dmaic.problem_statement,
        f"",
        "### CTQs",
    ]
    for c in dmaic.ctqs:
        lines.append(f"- {c}")

    lines += [
        "",
        "## 2. Market performance (MEASURE)",
        "",
        f"| KPI | Value |",
        f"|---|---|",
        f"| Projects | {bundle.kpis.total_projects} |",
        f"| Units launched | {sk['total_units']:,} |",
        f"| Units sold | {sk['units_sold']:,} |",
        f"| Units unsold | {sk['units_unsold']:,} |",
        f"| Absorption | {sk['absorption_pct']}% |",
        f"| Sigma (DPMO-based) | {sk['sigma_level']} |",
        f"| DPMO | {sk['dpmo']:,.0f} |",
        f"| At-risk projects (<70%) | {sk['at_risk_projects']} |",
        f"| Bookings (filtered) | {bundle.kpis.bookings:,} |",
        f"| Marketing spend (₹ Cr) | {bundle.kpis.marketing_spend_cr:,.2f} |",
        f"| Period sales value (₹ Cr) | {bundle.kpis.sales_value_cr:,.2f} |",
        "",
        "## 3. Competition blind spot (mentor ask)",
        "",
        f"- RERA approvals in catalog: **{comp.rera_count}**",
        f"- Upcoming / advertised: **{comp.upcoming_count}**",
        f"- Under construction projects: **{comp.uc_projects}**",
        f"- Unsold UC units: **{comp.unsold_uc_units:,}**",
        f"- Avg land price: **₹{comp.avg_land_psf:,.0f}/sqft**",
        "",
        "## 4. Location DSS (Phase 2)",
        "",
        f"- Zones scored: **{mk['areas_covered']}**",
        f"- Average price: **₹{mk['avg_price_psf']:,.0f}/sqft**",
        f"- AI top pick: **{mk['ai_top_pick']}**",
        f"- Highest growth area: **{mk['highest_growth_area']}**",
        f"- High-risk zones (<50 score): **{mk['high_risk_zones']}**",
        "",
        "## 5. Priority actions (IMPROVE)",
        "",
    ]

    at_risk = dmaic.at_risk.head(5)
    if at_risk.empty:
        lines.append("- No projects below absorption risk threshold under current filters.")
    else:
        lines.append("Focus interventions on:")
        for _, r in at_risk.iterrows():
            lines.append(
                f"- **{r['project']}** ({r['developer']}) — absorption {r['absorption_pct']}% · "
                f"unsold {int(r.get('units_unsold', 0))}"
            )

    lines += [
        "",
        "## 6. Decision sentence",
        "",
        "> Before launching or repricing in Bagaluru, review RERA crowding, upcoming ads, "
        "under-construction unsold stock, land cost, and buyer/channel mix in this brief — "
        "then validate interventions in Digital Twin and MONITOR via SPC.",
        "",
        "---",
        f"*{settings.APP_TITLE} · submission build*",
    ]
    return "\n".join(lines)


def competition_csv() -> pd.DataFrame:
    snap = build_competition_snapshot()
    return snap.upcoming.assign(layer="upcoming")
