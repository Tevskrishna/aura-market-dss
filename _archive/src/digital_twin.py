from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class TwinResult:
    months: list[int]
    baseline: list[float]
    intervention: list[float]
    revenue_baseline_cr: float
    revenue_intervention_cr: float
    recovery_cr: float


def run_segmented_twin(
    base_monthly_rate: float,
    months: int,
    price_psf: float,
    construction_progress: float,
    avg_ticket_lakhs: float,
    intervene_month: int | None = None,
    price_cut_pct: float = 0.0,
    subvention: bool = False,
) -> TwinResult:
    """SimPy-style discrete monthly sales with budget/premium/normal buyer segments.

    Uses Poisson arrivals per segment; does not require SimPy runtime for MVP
    (pure NumPy event engine — same segmented logic described in the DMAIC brief).
    """
    rng = np.random.default_rng(21)
    baseline = []
    intervent = []
    sold_b = 0.0
    sold_i = 0.0
    progress = construction_progress

    for m in range(1, months + 1):
        season = 1.0 + 0.12 * np.sin(2 * np.pi * m / 12)
        demand_idx = season * (0.85 + 0.15 * (progress / 100))

        # Segment weights
        budget_w = 0.35 * (1.1 if price_psf < 8500 else 0.7)
        premium_w = 0.25 * (0.7 + 0.6 * (progress / 100))
        normal_w = 0.40 * demand_idx
        total_w = budget_w + premium_w + normal_w

        lam = base_monthly_rate * (total_w / 1.0)
        sales_b = float(rng.poisson(max(lam, 0.1)))
        sold_b += sales_b
        baseline.append(sold_b)

        # Intervention path
        p = price_psf
        boost = 1.0
        if intervene_month and m >= intervene_month:
            p = price_psf * (1 - price_cut_pct / 100)
            if price_cut_pct > 0:
                boost *= 1.0 + min(price_cut_pct / 100 * 2.2, 0.55)
            if subvention:
                boost *= 1.18
            budget_w = 0.35 * (1.1 if p < 8500 else 0.75)
        lam_i = base_monthly_rate * boost * ((budget_w + premium_w + normal_w) / max(total_w, 0.1))
        sales_i = float(rng.poisson(max(lam_i, 0.1)))
        sold_i += sales_i
        intervent.append(sold_i)

        progress = min(progress + (100 - construction_progress) / months, 100)

    ticket_cr = avg_ticket_lakhs / 100.0
    rev_b = sold_b * ticket_cr
    rev_i = sold_i * ticket_cr
    return TwinResult(
        months=list(range(1, months + 1)),
        baseline=baseline,
        intervention=intervent,
        revenue_baseline_cr=round(rev_b, 2),
        revenue_intervention_cr=round(rev_i, 2),
        recovery_cr=round(rev_i - rev_b, 2),
    )
