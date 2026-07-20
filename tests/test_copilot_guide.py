"""Copilot guide — page-aware answers (no ML)."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from services.copilot_guide_service import answer_copilot


def test_copilot_start_and_purpose():
    a = answer_copilot("Where should I start?", module="Market Intelligence")
    assert "Executive Hub" in a
    b = answer_copilot("Summarize this page", module="Digital Twin")
    assert "strategy" in b.lower() or "Twin" in b or "what" in b.lower()


def test_copilot_metrics_glossary():
    t = answer_copilot("What is threat score?", module="Executive Hub")
    assert "0–100" in t or "0-100" in t or "Threat" in t
    g = answer_copilot("Why is the recommendation GO?", module="Executive Hub")
    assert "Hub" in g


def test_copilot_next_step():
    n = answer_copilot("Where should I go next?", module="Executive Hub")
    assert "Market" in n
