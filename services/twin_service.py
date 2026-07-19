"""
AURA-Market Digital Twin — segmented buyers + competitive cannibalization.

External rival launches divert budget/normal demand (competition blind spot).
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from config import settings


@dataclass
class TwinResult:
    months: list[int]
    baseline: list[float]
    intervention: list[float]
    cannibalized: list[float]
    revenue_baseline_cr: float
    revenue_intervention_cr: float
    revenue_cannibal_cr: float
    recovery_cr: float
    cannibal_loss_cr: float


def _simulate_path(
    *,
    base_monthly_rate: float,
    months: int,
    price_psf: float,
    construction_progress: float,
    intervene_month: int | None,
    price_cut_pct: float,
    subvention: bool,
    competitor_launch_month: int | None,
    competitor_price_psf: float | None,
    apply_rival: bool,
    own_intervene: bool,
    seed: int,
) -> tuple[list[float], float]:
    rng = np.random.default_rng(seed)
    cumulative: list[float] = []
    sold = 0.0
    progress = construction_progress

    for m in range(1, months + 1):
        season = 1.0 + 0.12 * np.sin(2 * np.pi * m / 12)
        demand_idx = season * (0.85 + 0.15 * (progress / 100))
        premium_w = 0.25 * (0.7 + 0.6 * (progress / 100))
        normal_w = 0.40 * demand_idx

        own_price = price_psf
        boost = 1.0
        if own_intervene and intervene_month and m >= intervene_month:
            own_price = price_psf * (1 - price_cut_pct / 100)
            if price_cut_pct > 0:
                boost *= 1.0 + min(price_cut_pct / 100 * 2.2, 0.55)
            if subvention:
                boost *= 1.18

        budget_w = 0.35 * (1.1 if own_price < 8500 else 0.7)
        total_w = max(budget_w + premium_w + normal_w, 0.05)

        rival_active = (
            apply_rival
            and competitor_launch_month is not None
            and competitor_price_psf is not None
            and m >= competitor_launch_month
            and float(competitor_price_psf) < own_price
        )
        if rival_active:
            gap = (own_price - float(competitor_price_psf)) / max(own_price, 1.0)
            budget_w *= 1.0 - min(0.75, settings.CANNIBAL_BUDGET_DIVERT_PCT + gap * 0.5)
            normal_w *= 1.0 - min(0.40, settings.CANNIBAL_NORMAL_DIVERT_PCT + gap * 0.25)

        tw = max(budget_w + premium_w + normal_w, 0.05)
        lam = base_monthly_rate * boost * (tw / max(total_w, 0.1))
        sold += float(rng.poisson(max(lam, 0.05)))
        cumulative.append(sold)
        progress = min(progress + (100 - construction_progress) / months, 100)

    return cumulative, sold


def run_twin_with_cannibalization(
    base_monthly_rate: float,
    months: int,
    price_psf: float,
    construction_progress: float,
    avg_ticket_lakhs: float,
    intervene_month: int | None = None,
    price_cut_pct: float = 0.0,
    subvention: bool = False,
    competitor_launch_month: int | None = None,
    competitor_price_psf: float | None = None,
    seed: int = 21,
) -> TwinResult:
    """
    baseline      = no rival, no own promo
    cannibalized  = rival launch steals demand (blind-spot loss)
    intervention  = own promo while rival is active (prescriptive recovery)
    """
    common = dict(
        base_monthly_rate=base_monthly_rate,
        months=months,
        price_psf=price_psf,
        construction_progress=construction_progress,
        intervene_month=intervene_month,
        price_cut_pct=price_cut_pct,
        subvention=subvention,
        competitor_launch_month=competitor_launch_month,
        competitor_price_psf=competitor_price_psf,
    )
    base_curve, sold_b = _simulate_path(**common, apply_rival=False, own_intervene=False, seed=seed)
    cannibal_curve, sold_c = _simulate_path(
        **common, apply_rival=bool(competitor_launch_month), own_intervene=False, seed=seed + 1
    )
    intervene_curve, sold_i = _simulate_path(
        **common, apply_rival=bool(competitor_launch_month), own_intervene=True, seed=seed + 2
    )
    if not competitor_launch_month:
        cannibal_curve, sold_c = base_curve, sold_b
        intervene_curve, sold_i = _simulate_path(**common, apply_rival=False, own_intervene=True, seed=seed + 2)

    ticket_cr = avg_ticket_lakhs / 100.0
    rev_b = sold_b * ticket_cr
    rev_i = sold_i * ticket_cr
    rev_c = sold_c * ticket_cr
    return TwinResult(
        months=list(range(1, months + 1)),
        baseline=base_curve,
        intervention=intervene_curve,
        cannibalized=cannibal_curve,
        revenue_baseline_cr=round(rev_b, 2),
        revenue_intervention_cr=round(rev_i, 2),
        revenue_cannibal_cr=round(rev_c, 2),
        recovery_cr=round(rev_i - rev_c, 2),
        cannibal_loss_cr=round(rev_b - rev_c, 2),
    )


def run_segmented_twin(
    base_monthly_rate: float,
    months: int,
    price_psf: float,
    construction_progress: float,
    avg_ticket_lakhs: float,
    intervene_month: int | None = None,
    price_cut_pct: float = 0.0,
    subvention: bool = False,
    competitor_launch_month: int | None = None,
    competitor_price_psf: float | None = None,
    seed: int = 21,
) -> TwinResult:
    """Backward-compatible alias used by Recommendations / older pages."""
    return run_twin_with_cannibalization(
        base_monthly_rate=base_monthly_rate,
        months=months,
        price_psf=price_psf,
        construction_progress=construction_progress,
        avg_ticket_lakhs=avg_ticket_lakhs,
        intervene_month=intervene_month,
        price_cut_pct=price_cut_pct,
        subvention=subvention,
        competitor_launch_month=competitor_launch_month,
        competitor_price_psf=competitor_price_psf,
        seed=seed,
    )
