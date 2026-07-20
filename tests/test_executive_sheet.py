"""Executive Decision Sheet adapters + model."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from services.adapters import get_adapter
from services.decision_brief_service import (
    DECISION_JOURNEY,
    brief_from_land,
    brief_from_launch,
    brief_from_market,
    brief_from_recommendations,
    brief_from_twin,
    next_after,
)
from services.launch_copilot_service import evaluate_launch
from services.margin_service import evaluate_land_decision


def test_journey_chain():
    assert len(DECISION_JOURNEY) == 11
    assert next_after("Executive Hub").label == "Market Intelligence"
    assert next_after("Decision Explanation").label == "SPC Control"
    assert next_after("Reports") is None
    assert DECISION_JOURNEY[0].label == "Executive Hub"
    assert DECISION_JOURNEY[-1].label == "Reports"


def test_brief_from_launch_maps_verdict():
    projects = get_adapter().projects()
    p = projects.iloc[0]["project"]
    v = evaluate_launch(project=p, my_price_psf=9000)
    brief = brief_from_launch(v)
    assert brief.risk_level in {"LOW", "MEDIUM", "HIGH", "CRITICAL"}
    assert brief.suggested_actions
    assert brief.next_step is not None
    assert "Executive" in brief.module or brief.module


def test_brief_from_land():
    d = evaluate_land_decision(assumed_sale_psf=9000)
    brief = brief_from_land(d)
    assert brief.risk_level
    assert d.verdict in brief.executive_summary


def test_brief_from_market_and_twin():
    b = brief_from_market(absorption_pct=72.0, at_risk=3, dpmo=200000, unsold=2000)
    assert b.risk_level in {"LOW", "MEDIUM", "HIGH", "CRITICAL"}
    t = brief_from_twin(project="X", cannibal_loss_cr=12.0, recovery_cr=4.0, enable_rival=True)
    assert t.financial_impact_cr == 12.0


def test_brief_from_recommendations():
    b = brief_from_recommendations(project="Demo", actions=["Cut price"], recoverable_units=12)
    assert b.next_step is not None
    assert "second" in (b.business_impact or "").lower() or "Hub" in (b.ai_recommendation or "")
    assert b.module == "Decision Explanation"
