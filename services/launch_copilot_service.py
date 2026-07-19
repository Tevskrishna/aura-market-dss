"""
Launch Decision Co-pilot — proprietary GO / HOLD / NO-GO engine.

Unique wedge (not a dashboard): answer one real-world decision —
"Can I launch (or reprice) at ₹X/sqft in Bagaluru this month?"

Fuses competition pressure + digital-twin rupee exposure + margin + SMC ROI
into a single Launch Threat Score (0–100) and three concrete actions.
"""
from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from config import settings
from services.adapters import get_adapter
from services.competition_service import build_competition_snapshot, launch_price_pressure
from services.map_service import map_home_kpis, scored_zones
from services.margin_service import build_margin_viability
from services.marketing_service import build_marketing_insights
from services.twin_service import run_twin_with_cannibalization
from models.market import FilterState
from datetime import date


@dataclass(frozen=True)
class LaunchVerdict:
    project: str
    developer: str
    my_price_psf: float
    threat_score: int  # 0 = safe, 100 = do not launch
    verdict: str  # GO | HOLD | NO-GO
    verdict_color: str
    headline: str
    blind_spot_loss_cr: float
    recovery_cr: float
    rival_name: str
    rival_price_psf: float
    high_threat_count: int
    uc_pressure_units: int
    margin_pct: float
    margin_label: str
    zone_tip: str
    smc_tip: str
    actions: list[str]
    factors: list[tuple[str, int, str]]  # label, points, note


def _score_band(score: int) -> tuple[str, str, str]:
    if score >= 70:
        return (
            "NO-GO",
            "#ff4b4b",
            "Do not publish this launch price — blind-spot risk is material.",
        )
    if score >= 40:
        return (
            "HOLD",
            "#f0b429",
            "Hold brochure print — reprice or intervene before going live.",
        )
    return (
        "GO",
        "#3dd68c",
        "Launch window looks viable — still MONITOR competition weekly.",
    )


def evaluate_launch(
    *,
    project: str,
    my_price_psf: float,
    intervene_cut_pct: float = 8.0,
    use_subvention: bool = True,
    rival_month: int = 3,
    horizon_months: int = 12,
) -> LaunchVerdict:
    adapter = get_adapter()
    projects = adapter.projects()
    upcoming = adapter.upcoming()
    row = projects[projects["project"] == project].iloc[0]
    price = float(my_price_psf)

    snap = build_competition_snapshot(adapter)
    threats = launch_price_pressure(upcoming, price)
    high = int((threats["threat"] == "High").sum()) if not threats.empty else 0
    med = int((threats["threat"] == "Medium").sum()) if not threats.empty else 0

    rival_name = "—"
    rival_price = price * 0.92
    if not threats.empty:
        cheap = threats.sort_values("indicative_price_psf").iloc[0]
        rival_name = str(cheap.get("project", "Rival"))
        rival_price = float(cheap["indicative_price_psf"])

    ticket = float(row["avg_unit_size_sqft"]) * price / 100_000
    base_rate = max(int(row["units_sold"] / 24), 6)
    twin = run_twin_with_cannibalization(
        base_monthly_rate=base_rate,
        months=horizon_months,
        price_psf=price,
        construction_progress=float(row["construction_progress_pct"]),
        avg_ticket_lakhs=ticket,
        intervene_month=4,
        price_cut_pct=float(intervene_cut_pct),
        subvention=use_subvention,
        competitor_launch_month=rival_month,
        competitor_price_psf=rival_price,
    )

    margins = build_margin_viability()
    mrow = margins[margins["project"] == project] if not margins.empty else pd.DataFrame()
    margin_pct = float(mrow.iloc[0]["margin_pct"]) if not mrow.empty else 15.0
    margin_label = str(mrow.iloc[0]["viability"]) if not mrow.empty else "Stressed"

    zones = scored_zones()
    mk = map_home_kpis(zones)

    filters = FilterState(
        builder=settings.ALL_BUILDERS_LABEL,
        project=settings.ALL_PROJECTS_LABEL,
        date_start=date(2019, 1, 1),
        date_end=date(2026, 12, 31),
        quarter=settings.ALL_QUARTERS_LABEL,
    )
    mkt = build_marketing_insights(filters)
    smc_tip = mkt.top_channel_hint or "Protect high-ROI channels; freeze bottom-quartile SMC spend."
    if mkt.reallocation:
        smc_tip = f"{mkt.reallocation[0]['action']} → {mkt.reallocation[0]['project']}"

    # --- Launch Threat Score (0–100): unique composite, not a raw KPI dump ---
    factors: list[tuple[str, int, str]] = []
    score = 0

    p_high = min(high * 18, 36)
    factors.append(("Nearby cheaper / near-price rivals", p_high, f"{high} High-threat upcoming"))
    score += p_high

    p_med = min(med * 6, 12)
    factors.append(("Medium-threat pipeline", p_med, f"{med} Medium upcoming"))
    score += p_med

    uc = snap.unsold_uc_units
    p_uc = 20 if uc > 800 else (12 if uc > 400 else (6 if uc > 150 else 0))
    factors.append(("Under-construction unsold stock", p_uc, f"{uc:,} UC unsold units"))
    score += p_uc

    loss = float(twin.cannibal_loss_cr)
    p_loss = 22 if loss >= 40 else (14 if loss >= 20 else (8 if loss >= 8 else 2))
    factors.append(("Simulated blind-spot ₹ loss", p_loss, f"₹{loss:.1f} Cr over {horizon_months} mo"))
    score += p_loss

    if margin_label == "Unviable":
        p_m = 18
    elif margin_label == "Stressed":
        p_m = 10
    else:
        p_m = 0
    factors.append(("Developer margin viability", p_m, f"{margin_pct:.1f}% · {margin_label}"))
    score += p_m

    abs_pct = float(row["absorption_pct"])
    p_abs = 12 if abs_pct < 55 else (8 if abs_pct < 70 else 0)
    factors.append(("Current absorption health", p_abs, f"{abs_pct:.0f}% absorbed today"))
    score += p_abs

    score = int(min(max(score, 0), 100))
    verdict, color, headline = _score_band(score)

    if verdict == "NO-GO":
        actions = [
            f"Cut launch price toward ₹{int(rival_price * 0.98):,}/sqft or below the nearest rival ({rival_name}).",
            f"Run Twin intervene now — modeled recovery ≈ ₹{twin.recovery_cr:.1f} Cr with {intervene_cut_pct:.0f}% cut"
            + (" + subvention" if use_subvention else "")
            + ".",
            "Freeze brochure / Meta spend until Competition High-threat count drops or margin stays Viable.",
        ]
    elif verdict == "HOLD":
        actions = [
            f"Reprice within ₹{int(price * 0.95):,}–{int(price):,}/sqft and re-check High-threat rivals.",
            f"Pre-arm intervention ({intervene_cut_pct:.0f}% cut) for month {rival_month} if {rival_name} goes live.",
            f"Shift SMC toward: {smc_tip}",
        ]
    else:
        actions = [
            f"Proceed near ₹{int(price):,}/sqft — still watch {rival_name} at ₹{int(rival_price):,}/sqft.",
            f"Diligence land / next site in {mk['ai_top_pick']} (Map AI top-pick).",
            "MONITOR weekly on SPC; keep Twin scenario saved as contingency.",
        ]

    return LaunchVerdict(
        project=str(row["project"]),
        developer=str(row["developer"]),
        my_price_psf=price,
        threat_score=score,
        verdict=verdict,
        verdict_color=color,
        headline=headline,
        blind_spot_loss_cr=round(loss, 2),
        recovery_cr=round(float(twin.recovery_cr), 2),
        rival_name=rival_name,
        rival_price_psf=round(rival_price, 0),
        high_threat_count=high,
        uc_pressure_units=uc,
        margin_pct=round(margin_pct, 1),
        margin_label=margin_label,
        zone_tip=str(mk["ai_top_pick"]),
        smc_tip=smc_tip,
        actions=actions,
        factors=factors,
    )


def verdict_markdown(v: LaunchVerdict) -> str:
    lines = [
        f"# Launch Decision — {v.project}",
        f"**Verdict: {v.verdict}** · Threat Score **{v.threat_score}/100**",
        "",
        v.headline,
        "",
        f"- Planned price: ₹{v.my_price_psf:,.0f}/sqft",
        f"- Nearest rival: {v.rival_name} @ ₹{v.rival_price_psf:,.0f}/sqft",
        f"- Blind-spot loss: ₹{v.blind_spot_loss_cr} Cr",
        f"- Recovery if intervene: ₹{v.recovery_cr} Cr",
        f"- Margin: {v.margin_pct}% ({v.margin_label})",
        "",
        "## Actions",
    ]
    for a in v.actions:
        lines.append(f"- {a}")
    lines += ["", "## Score factors"]
    for label, pts, note in v.factors:
        lines.append(f"- (+{pts}) {label} — {note}")
    return "\n".join(lines)
