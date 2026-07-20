"""
Decision brief adapters — map existing engines into DecisionBrief.
No duplicate scoring. Preserve LaunchVerdict / LandDecision / twin / sigma.
"""
from __future__ import annotations

from models.decision import DecisionBrief, JourneyStep
from services.launch_copilot_service import LaunchVerdict
from services.margin_service import LandDecision


# Guided Decision OS spine — one Continue chain (product experience)
DECISION_JOURNEY: list[JourneyStep] = [
    JourneyStep("Executive Hub", "app.py", "Should we launch?"),
    JourneyStep("Market Intelligence", "pages/1_Market_Overview.py", "Is demand healthy?"),
    JourneyStep("Competition & Land", "pages/2_Competition_Intelligence.py", "Will competitors hurt us?"),
    JourneyStep("Buyer Intelligence", "pages/3_Buyer_Analytics.py", "Who will buy?"),
    JourneyStep("Marketing Intelligence", "pages/4_Marketing_Intelligence.py", "Can marketing hit the target?"),
    JourneyStep("DMAIC Quality", "pages/5_DMAIC_Workspace.py", "Why are problems occurring?"),
    JourneyStep("Project Deep Dive", "pages/6_Builder_Deep_Dive.py", "Is the project financially healthy?"),
    JourneyStep("Scenario Engine", "pages/7_Digital_Twin.py", "What if strategy changes?"),
    JourneyStep("Decision Explanation", "pages/8_AI_Recommendations.py", "Why did the Hub decide this?"),
    JourneyStep("SPC Control", "pages/9_SPC_Control_Chart.py", "Can we trust this decision?"),
    JourneyStep("Reports", "pages/11_Executive_Reports.py", "Board decision pack"),
]

# Keep labels here (not components.*) so services never import UI modules at runtime
IC_DEMO_JOURNEY_LABELS: frozenset[str] = frozenset(
    {
        "Executive Hub",
        "Market Intelligence",
        "Competition & Land",
        "Scenario Engine",
        "Decision Explanation",
        "Reports",
    }
)


def active_journey() -> list[JourneyStep]:
    """IC Demo Mode uses the short spine; Quality Lab uses the full Continue chain."""
    try:
        import streamlit as st

        try:
            from streamlit.runtime.scriptrunner import get_script_run_ctx
        except ImportError:
            from streamlit.runtime.scriptrunner_utils.script_run_context import (  # type: ignore
                get_script_run_ctx,
            )

        # Bare pytest / scripts have no ScriptRunContext — keep full spine for unit tests
        if get_script_run_ctx() is None:
            return list(DECISION_JOURNEY)
        if bool(st.session_state.get("iq_ic_demo_mode", True)):
            return [s for s in DECISION_JOURNEY if s.label in IC_DEMO_JOURNEY_LABELS]
    except Exception:
        pass
    return list(DECISION_JOURNEY)


def journey_index(module_label: str) -> int:
    labels = [s.label for s in active_journey()]
    return labels.index(module_label) if module_label in labels else -1


def next_after(module_label: str) -> JourneyStep | None:
    steps = active_journey()
    labels = [s.label for s in steps]
    if module_label not in labels:
        return steps[1] if len(steps) > 1 else None
    i = labels.index(module_label)
    if i + 1 >= len(steps):
        return None
    return steps[i + 1]


def prev_before(module_label: str) -> JourneyStep | None:
    steps = active_journey()
    labels = [s.label for s in steps]
    if module_label not in labels:
        return None
    i = labels.index(module_label)
    if i <= 0:
        return None
    return steps[i - 1]


def _risk_from_verdict(verdict: str, score: int | None = None) -> str:
    v = (verdict or "").upper()
    if v in {"NO-GO", "PASS", "CRITICAL"} or (score is not None and score >= 70):
        return "CRITICAL" if v == "NO-GO" or (score or 0) >= 85 else "HIGH"
    if v in {"HOLD", "STRESSED"} or (score is not None and score >= 40):
        return "MEDIUM"
    if v in {"GO", "BUY", "VIABLE"}:
        return "LOW"
    return "MEDIUM"


def brief_from_launch(v: LaunchVerdict) -> DecisionBrief:
    insights = [
        f"Nearest rival {v.rival_name} at ₹{v.rival_price_psf:,.0f}/sqft",
        f"{v.high_threat_count} high-threat upcoming overlap(s) · UC pressure {v.uc_pressure_units:,} units",
        f"Margin {v.margin_pct}% ({v.margin_label}) · zone tip: {v.zone_tip}",
    ]
    if v.smc_tip:
        insights.append(v.smc_tip)
    drivers = [f"{label} (+{pts}): {note}" for label, pts, note in v.factors[:5]]
    return DecisionBrief(
        module="Executive Hub",
        executive_summary=f"{v.verdict} on {v.project} at ₹{v.my_price_psf:,.0f}/sqft — {v.headline}",
        key_insights=insights,
        business_impact=(
            f"Blind-spot exposure ≈ ₹{v.blind_spot_loss_cr} Cr if rival launches unchecked; "
            f"recoverable ≈ ₹{v.recovery_cr} Cr with intervene package."
        ),
        ai_recommendation=v.headline,
        risk_level=_risk_from_verdict(v.verdict, v.threat_score),
        risk_score=v.threat_score,
        suggested_actions=list(v.actions[:5]),
        financial_impact_label="Blind-spot loss (₹ Cr)",
        financial_impact_cr=float(v.blind_spot_loss_cr),
        confidence="Model · competition seed + twin + margin (see honesty banner)",
        drivers=drivers,
        next_step=next_after("Executive Hub"),
        honesty_notes=[
            "Competition layers may be seed until AURA_LIVE_*_URL is configured.",
        ],
    )


LAND_DILIGENCE_LABEL = {
    "BUY": "Proceed",
    "HOLD": "Caution",
    "PASS": "Walk",
}


def brief_from_land(d: LandDecision) -> DecisionBrief:
    diligence = LAND_DILIGENCE_LABEL.get(d.verdict, d.verdict)
    return DecisionBrief(
        module="Competition & Land",
        executive_summary=f"Land diligence · {diligence} · {d.micro_market} — {d.headline}",
        key_insights=[
            f"Land ₹{d.land_price_psf:,.0f}/sqft · exit ₹{d.assumed_sale_psf:,.0f}/sqft",
            f"Implied margin {d.margin_pct}% ({d.viability})",
            f"Upcoming ads {d.nearby_upcoming} · UC unsold {d.uc_unsold_nearby:,}",
        ],
        business_impact=(
            f"Loaded land ₹{d.loaded_land_psf:,.0f}/sqft + build ₹{d.construction_cost_psf:,.0f}/sqft "
            f"must clear target margin before LOI. Land diligence — not the Hub launch call."
        ),
        ai_recommendation=f"Land diligence: {diligence}. {d.headline}",
        risk_level=_risk_from_verdict(d.verdict),
        risk_score={"BUY": 25, "HOLD": 55, "PASS": 85}.get(d.verdict, 50),
        suggested_actions=list(d.actions[:5]),
        financial_impact_label="Implied margin (%)",
        financial_impact_cr=float(d.margin_pct),
        confidence="Seed land indices + local competition density",
        drivers=[f"Diligence: {diligence}", f"Viability: {d.viability}"],
        next_step=next_after("Competition & Land"),
        honesty_notes=[
            "Land prices are catalog indices, not a live title opinion. "
            "Proceed / Caution / Walk supports — does not replace — the Hub launch call."
        ],
    )


def brief_from_market(*, absorption_pct: float, at_risk: int, dpmo: float, unsold: int) -> DecisionBrief:
    if at_risk >= 5 or absorption_pct < 75:
        risk, rec = "HIGH", "Do not accelerate new launches until IMPROVE clears at-risk inventory."
    elif at_risk >= 2:
        risk, rec = "MEDIUM", "Hold brochure cadence — escalate at-risk projects this week."
    else:
        risk, rec = "LOW", "Market absorption healthy — protect price discipline."
    return DecisionBrief(
        module="Market Intelligence",
        executive_summary=f"Corridor absorption {absorption_pct:.1f}% · {at_risk} at-risk projects · DPMO {dpmo:,.0f}",
        key_insights=[
            f"Unsold pool {unsold:,} units (defect lens for Six Sigma)",
            f"At-risk (<70% absorption): {at_risk}",
            f"DPMO {dpmo:,.0f}",
        ],
        business_impact="High DPMO = capital locked in slow inventory — opportunity cost before next launch.",
        ai_recommendation=rec,
        risk_level=risk,
        risk_score=min(int(dpmo / 5000), 100),
        suggested_actions=[
            "Focus at-risk inventory in this workspace, then open Decision Explanation.",
            "Benchmark sold-out projects on Project Deep Dive before repricing.",
            "Pressure-test rival launch on Scenario Engine before print.",
        ],
        financial_impact_label="Unsold units (count)",
        financial_impact_cr=float(unsold),
        confidence="Validated project catalog",
        next_step=next_after("Market Intelligence"),
    )


def brief_from_twin(
    *,
    project: str,
    cannibal_loss_cr: float,
    recovery_cr: float,
    enable_rival: bool,
) -> DecisionBrief:
    if cannibal_loss_cr >= 15:
        risk = "HIGH"
    elif cannibal_loss_cr >= 5:
        risk = "MEDIUM"
    else:
        risk = "LOW"
    return DecisionBrief(
        module="Scenario Engine",
        executive_summary=(
            f"{project}: rival scenario loss ≈ ₹{cannibal_loss_cr} Cr; "
            f"intervention recovery ≈ ₹{recovery_cr} Cr."
        ),
        key_insights=[
            f"Unmitigated rival impact ₹{cannibal_loss_cr} Cr"
            + (" (rival on)" if enable_rival else " (rival off)"),
            f"Counter-offer recovery ₹{recovery_cr} Cr with cut/subvention package",
        ],
        business_impact="Scenario engine translates competition into directional ₹ Cr before brochure spend.",
        ai_recommendation=(
            "If recovery << loss, HOLD launch and deepen price/amenity intervene; else proceed with MONITOR."
            if cannibal_loss_cr > recovery_cr
            else "Intervention covers material rival damage — document package in board pack."
        ),
        risk_level=risk,
        risk_score=min(int(cannibal_loss_cr * 3), 100),
        suggested_actions=[
            "Lock winning intervene month + cut % before marketing spends.",
            "Export board pack with scenario figures attached.",
            "Return to Executive Hub and recompute Launch risk index.",
        ],
        financial_impact_label="Unmitigated rival impact (₹ Cr)",
        financial_impact_cr=float(cannibal_loss_cr),
        confidence="NumPy scenario engine (seed rates) — directional IC input",
        next_step=next_after("Scenario Engine"),
    )


def brief_from_recommendations(*, project: str, actions: list[str], recoverable_units: int) -> DecisionBrief:
    why = (
        f"Evidence explanation for the Hub call on {project}: "
        f"{len(actions)} supporting signals · ~{recoverable_units} units recoverable if Hub actions execute."
    )
    return DecisionBrief(
        module="Decision Explanation",
        executive_summary=why,
        key_insights=actions[:4] or ["No material defect signals — Hub MONITOR stands."],
        business_impact=(
            "This page explains WHY the Hub recommended GO / HOLD / NO-GO — "
            "it does not issue a second launch verdict."
        ),
        ai_recommendation=(
            "These factors support the Executive Hub decision. "
            "Return to Hub for the only final recommendation."
        ),
        risk_level="MEDIUM" if recoverable_units else "LOW",
        risk_score=min(recoverable_units, 100),
        suggested_actions=actions[:5] or ["Maintain MONITOR on SPC."],
        financial_impact_label="Est. recoverable units (evidence)",
        financial_impact_cr=float(recoverable_units),
        confidence="Rule + journey evidence — explains Hub; does not override Hub",
        next_step=next_after("Decision Explanation"),
        drivers=["Market", "Competition", "Buyer", "Marketing", "DMAIC", "Twin", "SPC"],
        honesty_notes=["Final launch recommendation lives only on Executive Hub."],
    )


def brief_from_marketing(*, total_spend_cr: float, avg_roi: float, cut_n: int) -> DecisionBrief:
    if cut_n >= 3 or avg_roi < 0.4:
        risk, rec = "HIGH", "Cut bottom-quartile SMC this week — redeploy to High ROI projects."
    elif cut_n >= 1:
        risk, rec = "MEDIUM", "Reallocate selectively via weekly allocator; protect top channel."
    else:
        risk, rec = "LOW", "Hold mix — scale High quartile carefully."
    return DecisionBrief(
        module="Marketing Intelligence",
        executive_summary=f"SMC ₹{total_spend_cr:.2f} Cr · avg ROI {avg_roi:.2f} · {cut_n} budget actions",
        key_insights=[
            f"Total spend ₹{total_spend_cr:.2f} Cr",
            f"Average ROI score {avg_roi:.2f}",
            f"{cut_n} projects tagged Budget action (bottom quartile)",
        ],
        business_impact="Blind SMC spend competes with price/construction capital — ROI quartile decides who keeps budget. Budget action ≠ Hub GO/HOLD.",
        ai_recommendation=rec,
        risk_level=risk,
        risk_score=min(cut_n * 15 + int((1 - min(avg_roi, 1)) * 40), 100),
        suggested_actions=[
            "Run weekly allocator and lock High-quartile share.",
            "Pause Dead/Q4 projects before next media cycle.",
            "Continue to DMAIC to frame the defect before Twin / Hub actions.",
        ],
        financial_impact_label="SMC spend (₹ Cr)",
        financial_impact_cr=float(total_spend_cr),
        confidence="Measured SMC workbook + booking outcomes",
        next_step=next_after("Marketing Intelligence"),
    )


def brief_from_buyer(*, bookings: int, top_channel: str, first_time_share: str = "") -> DecisionBrief:
    return DecisionBrief(
        module="Buyer Intelligence",
        executive_summary=f"{bookings:,} bookings in filter · top channel {top_channel or 'n/a'}",
        key_insights=[
            f"Confirmed bookings {bookings:,}",
            f"Primary channel signal: {top_channel or 'mixed'}",
            first_time_share or "Review age / native / family mix below",
        ],
        business_impact="Audience mix tells whether price cuts or NRI/investor campaigns move absorption.",
        ai_recommendation="Align brochure tone and channel mix to the dominant booking segment before raising SMC.",
        risk_level="MEDIUM" if bookings < 50 else "LOW",
        risk_score=40 if bookings < 50 else 20,
        suggested_actions=[
            "Protect top conversion channel in weekly marketing allocator.",
            "If first-time heavy — prioritize ticket-size redesign over luxury push.",
            "Return to Market Overview for absorption bands.",
        ],
        financial_impact_label="Bookings in view",
        financial_impact_cr=float(bookings),
        confidence="Measured booking Excels",
        next_step=next_after("Buyer Intelligence"),
    )


def brief_from_map(*, top_zone: str, high_risk: int, areas: int) -> DecisionBrief:
    risk = "HIGH" if high_risk >= 5 else ("MEDIUM" if high_risk >= 2 else "LOW")
    return DecisionBrief(
        module="Map Intelligence",
        executive_summary=f"Top suitability: {top_zone} · {high_risk} high-risk zones of {areas}",
        key_insights=[
            f"AI top pick · {top_zone}",
            f"High-risk zone count · {high_risk}",
            "What-if and radar tabs recompute live",
        ],
        business_impact="Location diligence before land LOI — flood/metro/price beat brochure aesthetics.",
        ai_recommendation=f"Prioritize diligence in {top_zone}; defer high-risk flood/access pockets.",
        risk_level=risk,
        risk_score=min(high_risk * 12, 100),
        suggested_actions=[
            "Run what-if on metro/highway before IC.",
            "Cross-check Competition land sheet on the same micro-market.",
            "Export zone shortlist into board pack.",
        ],
        financial_impact_label="High-risk zones",
        financial_impact_cr=float(high_risk),
        confidence="RF suitability · pseudo-labels — honesty banner applies",
        next_step=JourneyStep("Competition & Land", "pages/2_Competition_Intelligence.py", "Convert map pick into BUY/HOLD/PASS"),
        honesty_notes=["Map ML uses illustrative labels — not cadastral PropStack truth."],
    )


def brief_from_dmaic(*, absorption_pct: float, at_risk: int, unsold: int) -> DecisionBrief:
    return DecisionBrief(
        module="DMAIC Quality",
        executive_summary=f"DEFINE unsold defect · absorption {absorption_pct:.1f}% · {at_risk} at-risk · {unsold:,} unsold",
        key_insights=[
            "CTQs bound the quality call for inventory risk",
            f"Pareto focus on top unsold share",
            f"{at_risk} projects below absorption ATQ",
        ],
        business_impact="DMAIC frames the defect so IMPROVE is not opinion — it is measurable.",
        ai_recommendation="Complete MEASURE Pareto, then open Decision Explanation for IMPROVE evidence.",
        risk_level="HIGH" if at_risk >= 5 else "MEDIUM",
        risk_score=min(at_risk * 10, 100),
        suggested_actions=[
            "Own CTQs in the IC note.",
            "Escalate at-risk rows via Decision Explanation (Hub owns the call).",
            "Control via SPC after intervene.",
        ],
        financial_impact_label="Unsold units",
        financial_impact_cr=float(unsold),
        confidence="Six Sigma DEFINE/MEASURE on catalog",
        next_step=next_after("DMAIC Quality"),
    )


def brief_from_builder(*, developer: str, at_risk: int, absorption_pct: float) -> DecisionBrief:
    return DecisionBrief(
        module="Project Deep Dive",
        executive_summary=f"{developer}: absorption {absorption_pct:.1f}% · {at_risk} at-risk under brand",
        key_insights=[
            f"Developer filter · {developer}",
            f"At-risk count · {at_risk}",
            "GB forecast artifact loads from disk when available",
        ],
        business_impact="Brand-level risk concentrates capital — act project-by-project, not with blanket cuts.",
        ai_recommendation="Open each at-risk expander and validate material cuts on Scenario Engine.",
        risk_level="HIGH" if at_risk >= 2 else ("MEDIUM" if at_risk else "LOW"),
        risk_score=min(at_risk * 25, 100),
        suggested_actions=[
            "Review at-risk expanders for evidence levers (not a new verdict).",
            "Compare ML gap vs actual absorption.",
            "Continue to Scenario Engine, then Decision Explanation.",
        ],
        financial_impact_label="At-risk projects (count)",
        financial_impact_cr=float(at_risk),
        confidence="Catalog + GB artifact",
        next_step=next_after("Project Deep Dive"),
    )


def brief_from_spc(*, ooc: int, series_label: str) -> DecisionBrief:
    risk = "HIGH" if ooc >= 3 else ("MEDIUM" if ooc else "LOW")
    return DecisionBrief(
        module="SPC Control",
        executive_summary=f"{series_label}: {ooc} out-of-control / run signals in I-MR window",
        key_insights=[
            f"Series · {series_label}",
            f"OOC / Western Electric hits · {ooc}",
            "Forecast bands are near-term only",
        ],
        business_impact="Unstable velocity means marketing and price intervenes will not stick until process is controlled.",
        ai_recommendation="If OOC — HOLD launch spend and investigate special causes before SMC scale-up.",
        risk_level=risk,
        risk_score=min(ooc * 20, 100),
        suggested_actions=[
            "Document special causes for each OOC point.",
            "Align intervene with Scenario Engine package.",
            "Cross-check Forecasting horizon for the same series.",
        ],
        financial_impact_label="OOC signals (count)",
        financial_impact_cr=float(ooc),
        confidence="I-MR · d2=1.128",
        next_step=next_after("SPC Control"),
    )


def brief_from_forecast(*, horizon: int, last_yhat: float, series_label: str) -> DecisionBrief:
    return DecisionBrief(
        module="Demand Forecast",
        executive_summary=f"{series_label}: {horizon}-month outlook · near-term ŷ ≈ {last_yhat:.1f} units/mo",
        key_insights=[
            f"Horizon {horizon} months",
            f"Latest forecast point ≈ {last_yhat:.1f}",
            "Not a multi-year metro shock model",
        ],
        business_impact="Near-term forecast sets whether to pull launches forward or slow inventory release.",
        ai_recommendation="If trajectory softens — HOLD brochure cadence and revisit Co-pilot price.",
        risk_level="MEDIUM",
        risk_score=45,
        suggested_actions=[
            "Compare forecast to SPC stability.",
            "Feed soft outlook into Launch Threat Score.",
            "Export narrative into board pack.",
        ],
        financial_impact_label="Forecast units/mo (latest)",
        financial_impact_cr=float(last_yhat),
        confidence="Linear-seasonal short horizon",
        next_step=JourneyStep("Reports", "pages/11_Executive_Reports.py", "Board pack"),
        honesty_notes=["Mentor scope: near-term decisions — not city-cycle futures."],
    )


def weekly_actions_unified(
    *,
    launch_actions: list[str],
    project: str,
    max_items: int = 5,
) -> list[str]:
    """
    Single 'Do this week' narrative — Hub co-pilot actions first,
    then top AI recommendation lines for the same project (no second score).
    """
    out: list[str] = []
    for a in launch_actions:
        if a and a not in out:
            out.append(a)
        if len(out) >= max_items:
            return out[:max_items]
    try:
        from services.adapters import get_adapter
        from services.recommendation_engine import recommendations_for_row

        df = get_adapter().projects()
        if df.empty or project not in set(df["project"].tolist()):
            return out[:max_items]
        row = df[df["project"] == project].iloc[0]
        sold = df[df["absorption_pct"] >= 95]
        for r in recommendations_for_row(row, sold)[:3]:
            line = f"{r.get('issue', 'Signal')} → {r.get('action', '')}".strip()
            if line and line not in out:
                out.append(line)
            if len(out) >= max_items:
                break
    except Exception:
        pass
    return out[:max_items]
