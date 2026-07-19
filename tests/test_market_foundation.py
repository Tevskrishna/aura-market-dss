"""Unit tests for Market Overview foundation services."""
from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from config import settings
from models.market import FilterState
from services.data_loader import clear_catalog_cache, load_catalog
from services.data_validator import validate_dataframe
from services.market_service import build_market_bundle, compute_kpis


def test_validate_dataframe_missing_columns():
    df = pd.DataFrame({"a": [1]})
    errors, _ = validate_dataframe(df, ["a", "b"])
    assert any("Missing" in e for e in errors)


def test_catalog_loads_core_datasets():
    clear_catalog_cache()
    catalog = load_catalog()
    assert catalog.report is not None
    assert catalog.report.ready_for_market_overview
    assert catalog.has("projects")
    assert catalog.has("monthly_absorption")
    assert catalog.has("buyer_demographics")


def test_compute_kpis_smoke():
    clear_catalog_cache()
    catalog = load_catalog()
    projects = catalog.get("projects")
    bookings = catalog.get("buyer_demographics")
    marketing = catalog.get("marketing_spends") if catalog.has("marketing_spends") else pd.DataFrame()
    kpis = compute_kpis(projects, bookings, marketing, monthly=catalog.get("monthly_absorption"))
    assert kpis.total_projects > 0
    assert kpis.total_units > 0
    assert 0 <= kpis.absorption_rate_pct <= 100


def test_build_market_bundle_with_filters():
    clear_catalog_cache()
    filters = FilterState(
        builder=settings.ALL_BUILDERS_LABEL,
        project=settings.ALL_PROJECTS_LABEL,
        date_start=date(2023, 1, 1),
        date_end=date(2025, 12, 31),
        quarter=settings.ALL_QUARTERS_LABEL,
    )
    bundle = build_market_bundle(filters)
    assert bundle.kpis.total_projects >= 1
    assert isinstance(bundle.kpis.buyer_distribution, dict)
