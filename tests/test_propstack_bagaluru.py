"""PropStack Bagaluru ingest — catalog + KPI sanity."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from services.data_loader import clear_catalog_cache, load_catalog
from services.market_service import propstack_summary_row


def test_propstack_projects_match_micromarket_totals():
    clear_catalog_cache()
    catalog = load_catalog()
    assert catalog.report is not None
    assert catalog.report.ready_for_market_overview
    projects = catalog.get("projects")
    assert len(projects) >= 12
    assert int(projects["total_units"].sum()) == 10283
    sold = int(projects["units_sold"].sum())
    assert sold == 8542
    abs_pct = round(sold / 10283 * 100, 2)
    assert abs_pct == 83.07


def test_propstack_optional_layers_present():
    clear_catalog_cache()
    catalog = load_catalog()
    for key in (
        "micromarket_summary",
        "inventory_trend",
        "weighted_price_trend",
        "new_launches",
        "absorption_by_price_band",
    ):
        assert catalog.has(key), f"missing {key}"
    summary = propstack_summary_row(catalog)
    assert summary is not None
    assert int(summary["projects"]) == 12
    assert int(summary["total_units"]) == 10283
    assert float(summary["absorption_pct"]) == 83.07
