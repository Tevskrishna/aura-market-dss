"""DEMO 100% — SimulationEngine + weekly actions."""
from __future__ import annotations

from services.decision_brief_service import weekly_actions_unified
from services.simulation_engine import NumpySimulationEngine, get_simulation_engine, set_simulation_engine
from services.twin_service import TwinResult


def test_simulation_engine_numpy_default():
    eng = get_simulation_engine()
    assert isinstance(eng, NumpySimulationEngine)
    assert eng.name == "numpy"
    result = eng.run(
        base_monthly_rate=10,
        months=6,
        price_psf=9000,
        construction_progress=40,
        avg_ticket_lakhs=50,
        intervene_month=3,
        price_cut_pct=8,
        subvention=True,
        competitor_launch_month=2,
        competitor_price_psf=8000,
    )
    assert isinstance(result, TwinResult)
    assert len(result.months) == 6
    assert result.cannibal_loss_cr >= 0


def test_set_simulation_engine_swap():
    class Stub(NumpySimulationEngine):
        name = "stub"

    set_simulation_engine(Stub())
    assert get_simulation_engine().name == "stub"
    set_simulation_engine(None)
    assert get_simulation_engine().name == "numpy"


def test_weekly_actions_unified_prefers_launch():
    actions = weekly_actions_unified(
        launch_actions=["Cut price 5%", "Enable subvention"],
        project="__missing__",
        max_items=5,
    )
    assert actions[0] == "Cut price 5%"
    assert "Enable subvention" in actions
