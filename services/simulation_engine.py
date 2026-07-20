"""
SimulationEngine interface — plan Wave 5.

NumPy twin is the default implementation. SimPy (P2-3) plugs in later
without changing Hub / Twin / Recs call sites.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from services.twin_service import TwinResult, run_twin_with_cannibalization


class SimulationEngine(ABC):
    """Abstract digital-twin engine — no scoring duplication."""

    name: str = "abstract"

    @abstractmethod
    def run(
        self,
        *,
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
        raise NotImplementedError


class NumpySimulationEngine(SimulationEngine):
    """Illustrative NumPy Poisson scenario engine (honest — not SimPy DES)."""

    name = "numpy"

    def run(
        self,
        *,
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


_DEFAULT: Optional[SimulationEngine] = None


def get_simulation_engine() -> SimulationEngine:
    global _DEFAULT
    if _DEFAULT is None:
        _DEFAULT = NumpySimulationEngine()
    return _DEFAULT


def set_simulation_engine(engine: SimulationEngine | None) -> None:
    """Tests / future SimPy swap."""
    global _DEFAULT
    _DEFAULT = engine
