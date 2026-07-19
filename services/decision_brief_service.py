"""
Decision brief adapters — map existing engines into DecisionBrief.
No duplicate scoring. Preserve LaunchVerdict / LandDecision / twin / sigma.
"""
from __future__ import annotations

from models.decision import DecisionBrief, JourneyStep
from services.launch_copilot_service import LaunchVerdict
from services.margin_service import LandDecision


# CEO journey — Hub guides user forward (Product Team rule)
DECISION_JOURNEY: list[JourneyStep] = [
    JourneyStep("Executive Hub", "app.py", "Frame the launch call"),
    JourneyStep("Market Intelligence", "pages/1_Market_Overview.py", "Confirm demand / DPMO health"),
    JourneyStep("Competition & Land", "pages/2_Competition_Intelligence.py", "Blind spot + land BUY/HOLD/PASS"),
    JourneyStep("Marketing Intelligence", "pages/4_Marketing_Intelligence.py", "Should we raise SMC?"),
    JourneyStep("AI Recommendations", "pages/8_AI_Recommendations.py", "Prescribe project actions"),
    JourneyStep("Digital Twin", "pages/7_Digital_Twin.py", "Pressure-test ₹ Cr impact"),
    JourneyStep("Reports", "pages/11_Executive_Reports.py", "Board pack PDF"),
]


def next_after(module_label: str) -> JourneyStep | None:
    labels = [s.label for s in DECISION_JOURNEY]
    if module_label not in labels:
        # Best-effort: Hub next by default
        return DECISION_JOURNEY[1]
    i = labels.index(module_label)
    if i + 1 >= len(DECISION_JOURNEY):
        return None
    return DECISION_JOURNEY[i + 1]


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


def brief_from_land(d: LandDecision) -> DecisionBrief:
    return DecisionBrief(
        module="Competition & Land",
        executive_summary=f"{d.verdict} · {d.micro_market} — {d.headline}",
        key_insights=[
            f"Land ₹{d.land_price_psf:,.0f}/sqft · exit ₹{d.assumed_sale_psf:,.0f}/sqft",
            f"Implied margin {d.margin_pct}% ({d.viability})",
            f"Upcoming ads {d.nearby_upcoming} · UC unsold {d.uc_unsold_nearby:,}",
        ],
        business_impact=(
            f"Loaded land ₹{d.loaded_land_psf:,.0f}/sqft + build ₹{d.construction_cost_psf:,.0f}/sqft "
            f"must clear target margin before LOI."
        ),
        ai_recommendation=d.headline,
        risk_level=_risk_from_verdict(d.verdict),
        risk_score={"BUY": 25, "HOLD": 55, "PASS": 85}.get(d.verdict, 50),
        suggested_actions=list(d.actions[:5]),
        financial_impact_label="Margin at assumed exit (%)",
        financial_impact_cr=float(d.margin_pct),
        confidence="Seed land indices + local competition density",
        drivers=[f"Viability: {d.viability}", f"Verdict: {d.verdict}"],
        next_step=JourneyStep(
            "Marketing Intelligence",
            "pages/4_Marketing_Intelligence.py",
            "If BUY/HOLD — size pre-launch SMC only after land diligence",
        ),
        honesty_notes=["Land prices are catalog indices, not a live title opinion."],
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
            "Focus at-risk inventory in this workspace, then open AI Recommendations.",
            "Benchmark sold-out projects on Builder Deep Dive before repricing.",
            "Pressure-test rival launch on Digital Twin before print.",
        ],
        financial_impact_label="Unsold units (inventory risk)",
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
        module="Digital Twin",
        executive_summary=(
            f"{project}: rival scenario loss ≈ ₹{cannibal_loss_cr} Cr; "
            f"intervention recovery ≈ ₹{recovery_cr} Cr."
        ),
        key_insights=[
            f"Blind-spot loss ₹{cannibal_loss_cr} Cr" + (" (rival on)" if enable_rival else " (rival off)"),
            f"Recovery vs rival ₹{recovery_cr} Cr with cut/subvention package",
        ],
        business_impact="Twin translates competition into rupees before brochure money is spent.",
        ai_recommendation=(
            "If recovery << loss, HOLD launch and deepen price/amenity intervene; else proceed with MONITOR."
            if cannibal_loss_cr > recovery_cr
            else "Intervention covers material rival damage — document package in board pack."
        ),
        risk_level=risk,
        risk_score=min(int(cannibal_loss_cr * 3), 100),
        suggested_actions=[
            "Lock winning intervene month + cut % before marketing spends.",
            "Export board pack with twin figures attached.",
            "Return to Executive Hub and recompute Launch Threat Score.",
        ],
        financial_impact_label="Blind-spot loss (₹ Cr)",
        financial_impact_cr=float(cannibal_loss_cr),
        confidence="NumPy twin (seed rates) — directional IC input",
        next_step=next_after("Digital Twin"),
    )


def brief_from_recommendations(*, project: str, actions: list[str], recoverable_units: int) -> DecisionBrief:
    return DecisionBrief(
        module="AI Recommendations",
        executive_summary=f"{project}: {len(actions)} prescribe actions · est. recoverable {recoverable_units} units",
        key_insights=actions[:4] or ["No material defect signals — monitor monthly."],
        business_impact=f"Estimated recoverable inventory ≈ {recoverable_units} units if actions execute this fortnight.",
        ai_recommendation=actions[0] if actions else "Hold price; pace construction CRM.",
        risk_level="MEDIUM" if recoverable_units else "LOW",
        risk_score=min(recoverable_units, 100),
        suggested_actions=actions[:5] or ["Maintain MONITOR on SPC."],
        financial_impact_label="Est. recoverable units",
        financial_impact_cr=float(recoverable_units),
        confidence="Rule + benchmark engine (augmented ML on Builder)",
        next_step=next_after("AI Recommendations"),
        drivers=["Price", "Delay", "Unit size", "Segment", "Brand", "Stage"],
    )
