"""CEO Morning Loop — decision context + board pack Section 0."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from services.decision_context import (
    CONTEXT_KEY,
    clear_decision_context,
    context_banner_text,
    format_relative_age,
    get_decision_context,
    has_decision_context,
    save_decision_context,
)
from services.report_service import build_executive_markdown, resolve_open_launch
from services.twin_service import twin_preset_params


def test_save_and_get_decision_context():
    bag: dict = {}
    payload = save_decision_context(
        project="Demo Towers",
        my_price_psf=9200,
        cut_pct=8,
        subvention=True,
        rival_month=3,
        intervene_month=4,
        horizon_months=12,
        verdict="HOLD",
        threat_score=55,
        blind_spot_loss_cr=12.5,
        recovery_cr=4.2,
        session=bag,
    )
    assert bag[CONTEXT_KEY]["project"] == "Demo Towers"
    assert payload["verdict"] == "HOLD"
    got = get_decision_context(bag)
    assert got is not None
    assert got["my_price_psf"] == 9200.0
    assert has_decision_context(bag)
    banner = context_banner_text(got) or ""
    assert "Continuing Hub" in banner
    assert "Updated" in banner
    clear_decision_context(bag)
    assert not has_decision_context(bag)


def test_format_relative_age():
    now = datetime(2026, 7, 20, 12, 0, 0, tzinfo=timezone.utc)
    assert format_relative_age(None) == "No open decision yet"
    assert format_relative_age("not-a-date") == "No open decision yet"
    just = (now - timedelta(seconds=10)).isoformat()
    assert format_relative_age(just, now=now) == "Updated just now"
    mins = (now - timedelta(minutes=4)).isoformat()
    assert format_relative_age(mins, now=now) == "Updated 4m ago"
    hours = (now - timedelta(hours=2)).isoformat()
    assert format_relative_age(hours, now=now) == "Updated 2h ago"
    days = (now - timedelta(days=3)).isoformat()
    assert format_relative_age(days, now=now) == "Updated 3d ago"


def test_twin_prefers_hub_params_in_presets():
    intervene = twin_preset_params(
        "Intervene",
        hub_cut=12,
        hub_subvention=False,
        hub_intervene=5,
        hub_rival=2,
        horizon=12,
    )
    assert intervene["cut_pct"] == 12.0
    assert intervene["subvention"] is False
    assert intervene["intervene_month"] == 5
    assert intervene["enable_rival"] is True

    blind = twin_preset_params("Blind spot", hub_rival=2, horizon=12)
    assert blind["enable_rival"] is True
    assert blind["intervene_month"] == 0
    assert blind["cut_pct"] == 0.0

    hold = twin_preset_params("Hold")
    assert hold["enable_rival"] is False
    assert hold["intervene_month"] == 0


def test_board_pack_section_zero_from_hub_context():
    bag: dict = {}
    projects = __import__("services.adapters", fromlist=["get_adapter"]).get_adapter().projects()
    assert not projects.empty
    project = str(projects.iloc[0]["project"])
    save_decision_context(
        project=project,
        my_price_psf=9500,
        cut_pct=10,
        subvention=True,
        rival_month=3,
        intervene_month=4,
        horizon_months=12,
        verdict="GO",
        threat_score=30,
        blind_spot_loss_cr=1.0,
        recovery_cr=0.5,
        session=bag,
    )
    v, from_hub = resolve_open_launch(bag)
    assert from_hub is True
    assert v.project == project
    assert float(v.my_price_psf) == 9500.0

    md = build_executive_markdown(session=bag)
    assert "## 0. Open Decision (CEO Hub)" in md
    assert "Locked from Executive Hub session" in md
    assert project in md
    assert "9500" in md or "9,500" in md


def test_board_pack_defaults_without_context():
    bag: dict = {}
    v, from_hub = resolve_open_launch(bag)
    assert from_hub is False
    md = build_executive_markdown(session=bag)
    assert "## 0. Open Decision (CEO Hub)" in md
    assert "catalog defaults" in md.lower() or "Using catalog defaults" in md
