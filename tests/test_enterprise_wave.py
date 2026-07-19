"""Enterprise wave — hybrid adapter, sqlite, env auth."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from config import settings
from config.auth import verify_credentials
from services.adapters import HybridCatalogAdapter, get_adapter
from services.sqlite_store import load_catalog_from_sqlite, sync_catalog_to_sqlite


def test_default_adapter_is_hybrid_or_safe():
    a = get_adapter()
    assert a.meta().mode in {"local", "hybrid", "live", "live-fallback"}
    assert not a.projects().empty


def test_hybrid_local_sample_overlay():
    prev = settings.LIVE_RERA_URL
    try:
        settings.LIVE_RERA_URL = "data/live_samples/rera.json"
        h = HybridCatalogAdapter()
        assert not h.rera().empty
        assert "rera_projects" in h.meta().live_layers
    finally:
        settings.LIVE_RERA_URL = prev


def test_sqlite_roundtrip(tmp_path):
    path = tmp_path / "cat.sqlite"
    sync_catalog_to_sqlite(path)
    cat = load_catalog_from_sqlite(path)
    assert cat.has("projects")
    assert not cat.get("projects").empty


def test_auth_env_passwords():
    assert verify_credentials("admin", "admin123") is not None
    assert verify_credentials("admin", "wrong") is None
    assert verify_credentials("demo", "demo123") is not None
