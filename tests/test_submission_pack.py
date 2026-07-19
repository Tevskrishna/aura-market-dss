"""AURA-Market / submission-pack tests."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from config import settings
from services.map_service import scored_zones, map_home_kpis
from services.report_service import build_executive_markdown
from services.competition_service import build_competition_snapshot
from services.margin_service import build_margin_viability, margin_kpis
from services.twin_service import run_twin_with_cannibalization
from services.buyer_service import build_buyer_insights
from services.data_loader import clear_catalog_cache


def test_branding():
    assert "AURA-Market" in settings.APP_TITLE
    assert settings.APP_SHORT_NAME == "AURA-Market"


def test_map_zones_cover_bengaluru():
    z = scored_zones()
    assert len(z) >= 20
    k = map_home_kpis(z)
    assert k["areas_covered"] == len(z)


def test_competition_layers_present():
    s = build_competition_snapshot()
    assert s.rera_count >= 5
    assert s.upcoming_count >= 3


def test_margin_viability_index():
    m = build_margin_viability()
    assert not m.empty
    k = margin_kpis(m)
    assert k["viable"] + k["stressed"] + k["unviable"] == len(m)


def test_cannibalization_loss():
    r = run_twin_with_cannibalization(12, 12, 9500, 60, 90, 4, 10, True, 3, 8200)
    assert r.cannibal_loss_cr >= 0
    assert len(r.cannibalized) == 12


def test_audience_demographics():
    clear_catalog_cache()
    i = build_buyer_insights()
    assert i.total_bookings > 0
    assert not i.age_profile.empty
    assert not i.native_mix.empty


def test_executive_brief_content():
    md = build_executive_markdown()
    assert "Competition blind spot" in md
