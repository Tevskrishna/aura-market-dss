"""
Executive report generation — submission-ready summaries from shared services.
"""
from __future__ import annotations

from datetime import date
from html import escape

import pandas as pd

from config import settings
from models.market import FilterState
from services.adapters import get_adapter
from services.competition_service import build_competition_snapshot
from services.decision_brief_service import brief_from_launch
from services.decision_context import get_decision_context
from services.dmaic_service import build_dmaic_snapshot
from services.launch_copilot_service import evaluate_launch
from services.map_service import map_home_kpis, scored_zones
from services.marketing_service import build_marketing_insights
from services.market_service import build_market_bundle
from services.recommendation_engine import recommendations_for_row
from services.sigma_service import market_kpis


def default_filters() -> FilterState:
    return FilterState(
        builder=settings.ALL_BUILDERS_LABEL,
        project=settings.ALL_PROJECTS_LABEL,
        date_start=date(2022, 12, 1),
        date_end=date(2025, 11, 30),
        quarter=settings.ALL_QUARTERS_LABEL,
    )


def resolve_open_launch(
    session: dict | None = None,
) -> tuple[object, bool]:
    """
    Rebuild Hub LaunchVerdict from session context (or catalog defaults).
    Returns (verdict, from_hub_context).
    """
    ctx = get_decision_context(session)
    projects = get_adapter().projects()
    if projects.empty:
        raise RuntimeError("No projects in catalog for board pack")
    if ctx and ctx.get("project") in set(projects["project"].tolist()):
        v = evaluate_launch(
            project=str(ctx["project"]),
            my_price_psf=float(ctx.get("my_price_psf", 9000)),
            intervene_cut_pct=float(ctx.get("cut_pct", 8)),
            use_subvention=bool(ctx.get("subvention", True)),
            rival_month=int(ctx.get("rival_month", 3)),
            horizon_months=int(ctx.get("horizon_months", 12)),
        )
        return v, True
    project = str(projects.iloc[0]["project"])
    price = float(projects.iloc[0]["price_psf"])
    v = evaluate_launch(project=project, my_price_psf=price)
    return v, False


def _open_decision_markdown(session: dict | None = None) -> list[str]:
    verdict, from_hub = resolve_open_launch(session)
    brief = brief_from_launch(verdict)
    source = (
        "Locked from Executive Hub session"
        if from_hub
        else "Using catalog defaults — open Executive Hub to lock today’s call"
    )
    lines = [
        "## 0. Open Decision (CEO Hub)",
        "",
        f"**Source:** {source}  ",
        f"**Verdict:** **{verdict.verdict}** on **{verdict.project}** at ₹{verdict.my_price_psf:,.0f}/sqft  ",
        f"**Threat score:** {verdict.threat_score}  ",
        f"**Risk:** {brief.risk_level}  ",
        f"**Blind-spot loss:** ₹{verdict.blind_spot_loss_cr} Cr  ",
        f"**Recoverable with intervene:** ₹{verdict.recovery_cr} Cr  ",
        f"**AI call:** {brief.ai_recommendation}  ",
        f"**Confidence:** {brief.confidence}",
        "",
        "### Do this week",
    ]
    for a in list(verdict.actions)[:3]:
        lines.append(f"- {a}")
    if brief.honesty_notes:
        lines.append("")
        lines.append(f"*{brief.honesty_notes[0]}*")
    lines.append("")
    return lines


def build_executive_markdown(
    filters: FilterState | None = None,
    session: dict | None = None,
) -> str:
    filters = filters or default_filters()
    bundle = build_market_bundle(filters)
    sk = market_kpis(bundle.projects)
    dmaic = build_dmaic_snapshot(filters)
    comp = build_competition_snapshot()
    zones = scored_zones()
    mk = map_home_kpis(zones)
    adapter = get_adapter().meta()
    mkt = build_marketing_insights(filters)

    lines = [
        f"# Executive Decision Brief — {settings.COMPANY_NAME}",
        "",
        f"**Generated:** {date.today().isoformat()}  ",
        f"**Micro-market:** {settings.MICRO_MARKET_DEFAULT}  ",
        f"**Data mode:** {adapter.mode} — {adapter.description}",
        "",
    ]
    lines += _open_decision_markdown(session)
    lines += [
        "## 1. Situation (DEFINE)",
        "",
        dmaic.problem_statement,
        "",
        "### CTQs",
    ]
    for c in dmaic.ctqs:
        lines.append(f"- {c}")

    lines += [
        "",
        "## 2. Market performance (MEASURE)",
        "",
        "| KPI | Value |",
        "|---|---|",
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
        "## 4. Marketing ROI (SMC)",
        "",
        f"- Total SMC spend: **₹{mkt.total_spend_cr:,.2f} Cr**",
        f"- SMC share rows utilized: **{len(mkt.share_long):,}**",
    ]
    if mkt.reallocation:
        lines.append("- Reallocation priorities:")
        for r in mkt.reallocation[:5]:
            lines.append(f"  - **{r['project']}** — {r['action']} ({r['issue']})")
    if mkt.top_channel_hint:
        lines.append(f"- {mkt.top_channel_hint}")

    lines += [
        "",
        "## 5. Location DSS (Phase 2)",
        "",
        f"- Zones scored: **{mk['areas_covered']}**",
        f"- Average price: **₹{mk['avg_price_psf']:,.0f}/sqft**",
        f"- AI top pick: **{mk['ai_top_pick']}**",
        f"- Highest growth area: **{mk['highest_growth_area']}**",
        f"- High-risk zones (<50 score): **{mk['high_risk_zones']}**",
        "",
        "## 6. Priority actions (IMPROVE)",
        "",
    ]

    at_risk = dmaic.at_risk.head(5)
    sold_out = bundle.projects[bundle.projects["absorption_pct"] >= settings.ABSORPTION_HEALTHY_PCT]
    if at_risk.empty:
        lines.append("- No projects below absorption risk threshold under current filters.")
    else:
        lines.append("Focus interventions on:")
        for _, r in at_risk.iterrows():
            lines.append(
                f"- **{r['project']}** ({r.get('developer', '')}) — absorption {r['absorption_pct']}% · "
                f"unsold {int(r.get('units_unsold', 0))}"
            )
            full = bundle.projects[bundle.projects["project"] == r["project"]]
            if full.empty:
                continue
            for rec in recommendations_for_row(full.iloc[0], sold_out)[:2]:
                lines.append(f"  - Action: **{rec['action']}** — {rec['detail']}")

    lines += [
        "",
        "## 7. Decision sentence",
        "",
        "> Before launching or repricing in Bagaluru, review RERA crowding, upcoming ads, "
        "under-construction unsold stock, land cost, SMC ROI quartiles, and buyer/channel mix — "
        "then validate interventions in Digital Twin and MONITOR via SPC.",
        "",
        "---",
        f"*{settings.APP_TITLE} · submission-ready build*",
    ]
    return "\n".join(lines)


def build_executive_html(
    filters: FilterState | None = None,
    session: dict | None = None,
) -> str:
    """Printable HTML brief (open in browser → Print to PDF)."""
    md = build_executive_markdown(filters, session=session)
    body_parts: list[str] = []
    for line in md.splitlines():
        if line.startswith("# "):
            body_parts.append(f"<h1>{escape(line[2:])}</h1>")
        elif line.startswith("## "):
            body_parts.append(f"<h2>{escape(line[3:])}</h2>")
        elif line.startswith("### "):
            body_parts.append(f"<h3>{escape(line[4:])}</h3>")
        elif line.startswith("> "):
            body_parts.append(f"<blockquote>{escape(line[2:])}</blockquote>")
        elif line.startswith("- "):
            body_parts.append(f"<li>{escape(line[2:])}</li>")
        elif line.startswith("  - "):
            body_parts.append(f'<li class="sub">{escape(line[4:])}</li>')
        elif line.startswith("|") and "---" not in line:
            cells = [c.strip() for c in line.strip("|").split("|")]
            tds = "".join(f"<td>{escape(c)}</td>" for c in cells)
            body_parts.append(f"<tr>{tds}</tr>")
        elif line.strip() == "---":
            body_parts.append("<hr/>")
        elif line.strip():
            body_parts.append(f"<p>{escape(line)}</p>")
    body = "\n".join(body_parts)
    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"/>
<title>AURA-Market Executive Brief</title>
<style>
body {{ font-family: Segoe UI, Inter, sans-serif; max-width: 860px; margin: 2rem auto; color: #111; line-height: 1.45; padding: 0 1rem; }}
h1 {{ font-size: 1.6rem; }} h2 {{ font-size: 1.2rem; margin-top: 1.4rem; border-bottom: 1px solid #ddd; padding-bottom: 0.25rem; }}
table {{ border-collapse: collapse; width: 100%; margin: 0.6rem 0; }}
td {{ border: 1px solid #ccc; padding: 0.35rem 0.5rem; font-size: 0.92rem; }}
blockquote {{ background: #f4f4f5; border-left: 4px solid #ff4b4b; padding: 0.7rem 1rem; }}
li {{ margin: 0.25rem 0; }} li.sub {{ margin-left: 1rem; list-style: circle; }}
@media print {{ body {{ margin: 0.6rem; }} }}
</style></head><body>{body}</body></html>"""


def competition_csv() -> pd.DataFrame:
    snap = build_competition_snapshot()
    return snap.upcoming.assign(layer="upcoming")


def build_executive_pdf(
    filters: FilterState | None = None,
    session: dict | None = None,
) -> bytes:
    """
    Board pack PDF — same narrative as markdown/HTML brief.
    Uses fpdf2 core fonts (latin-1); unicode is transliterated.
    """
    filters = filters or default_filters()
    md = build_executive_markdown(filters, session=session)
    try:
        from fpdf import FPDF
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("fpdf2 is required for PDF export; pip install fpdf2") from exc

    def _safe(text: str) -> str:
        repl = {
            "\u2014": "-",
            "\u2013": "-",
            "\u2018": "'",
            "\u2019": "'",
            "\u201c": '"',
            "\u201d": '"',
            "\u20b9": "INR ",
            "\u2022": "*",
            "\xa0": " ",
        }
        for a, b in repl.items():
            text = text.replace(a, b)
        text = text.replace("**", "").replace("—", "-").replace("–", "-").replace("₹", "INR ")
        return text.encode("latin-1", errors="replace").decode("latin-1")

    pdf = FPDF(format="A4", unit="mm")
    pdf.set_margins(14, 14, 14)
    pdf.set_auto_page_break(auto=True, margin=14)
    pdf.add_page()

    def _line(text: str, *, bold: bool = False, size: int = 9) -> None:
        pdf.set_x(pdf.l_margin)
        style = "B" if bold else ""
        pdf.set_font("Helvetica", style, size)
        usable = pdf.epw
        if usable < 10:
            pdf.set_x(pdf.l_margin)
            usable = pdf.w - pdf.l_margin - pdf.r_margin
        pdf.multi_cell(usable, 5, _safe(text))

    _line("AURA-Market - Board Decision Pack", bold=True, size=14)
    _line(f"Generated: {date.today().isoformat()} | Micro-market: {settings.MICRO_MARKET_DEFAULT}", size=9)
    pdf.ln(2)

    for line in md.splitlines():
        raw = line.rstrip()
        if not raw:
            pdf.ln(2)
            continue
        text = raw
        bold = False
        size = 9
        if text.startswith("# "):
            pdf.ln(3)
            bold, size, text = True, 12, text[2:]
        elif text.startswith("## "):
            pdf.ln(2)
            bold, size, text = True, 11, text[3:]
        elif text.startswith("### "):
            bold, size, text = True, 10, text[4:]
        elif text.startswith("|"):
            size = 8
            text = " | ".join(c.strip() for c in text.strip("|").split("|"))
        elif text.startswith("- "):
            text = "* " + text[2:]
        elif text.startswith("> "):
            text = text[2:]
        _line(text, bold=bold, size=size)

    out = pdf.output()
    if isinstance(out, (bytes, bytearray)):
        return bytes(out)
    return str(out).encode("latin-1", errors="replace")
