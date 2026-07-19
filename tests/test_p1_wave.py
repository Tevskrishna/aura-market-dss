"""P1 feature verification — land sheet, allocator, ML persist, PDF, repository."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from repositories.catalog_repo import get_catalog_repository
from services.adapters import get_adapter
from services.margin_service import evaluate_land_decision
from services.marketing_service import build_marketing_insights, weekly_budget_allocation
from services.recommendation_engine import fit_gb_forecast, gb_artifact_status
from services.report_service import build_executive_pdf, default_filters
from models.market import FilterState
from config import settings
from datetime import date


def test_land_decision_sheet():
    d = evaluate_land_decision(assumed_sale_psf=9000)
    assert d.verdict in {"BUY", "HOLD", "PASS"}
    assert d.margin_pct == d.margin_pct  # not NaN
    assert len(d.actions) >= 2


def test_weekly_allocator_sums_to_budget():
    filters = FilterState(
        builder=settings.ALL_BUILDERS_LABEL,
        project=settings.ALL_PROJECTS_LABEL,
        date_start=date(2022, 12, 1),
        date_end=date(2025, 11, 30),
        quarter=settings.ALL_QUARTERS_LABEL,
    )
    insights = build_marketing_insights(filters)
    budget = 1.5
    alloc = weekly_budget_allocation(insights.roi, weekly_budget_cr=budget)
    assert not alloc.empty
    assert abs(float(alloc["allocated_cr"].sum()) - budget) < 0.05


def test_gb_artifact_persists():
    df = get_adapter().projects()
    out1, score1, _ = fit_gb_forecast(df, force_retrain=True)
    assert score1 == score1
    assert gb_artifact_status()["artifact_exists"]
    out2, score2, _ = fit_gb_forecast(df, force_retrain=False)
    assert out2.attrs.get("model_loaded_from_disk") is True
    assert abs(score1 - score2) < 1e-9
    assert len(out1) == len(out2)


def test_board_pack_pdf_bytes():
    pdf = build_executive_pdf(default_filters())
    assert isinstance(pdf, (bytes, bytearray))
    assert len(pdf) > 500
    assert pdf[:4] == b"%PDF"


def test_catalog_repository_wraps_adapter():
    repo = get_catalog_repository()
    assert not repo.projects().empty
    assert repo.meta().mode in {"local", "live"}
