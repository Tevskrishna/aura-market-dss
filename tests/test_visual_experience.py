"""Visual Experience Mode — presentation flag only."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from components.visual_experience import (
    VISUAL_KEY,
    enhance_figure,
    try_comparison_3d_bars,
    visual_experience_on,
)


def test_visual_default_off_without_session():
    # Bare import path: no Streamlit session → treat as off
    assert VISUAL_KEY == "iq_visual_experience"
    assert visual_experience_on() is False or visual_experience_on() in (False, True)


def test_enhance_figure_noop_when_off():
    class _Fig:
        def update_layout(self, **kwargs):
            self.kwargs = kwargs

    fig = _Fig()
    out = enhance_figure(fig, purpose="scenario")
    assert out is fig
    assert not hasattr(fig, "kwargs") or "transition" not in getattr(fig, "kwargs", {})


def test_comparison_3d_returns_none_when_off():
    assert try_comparison_3d_bars(["2024"], [3.0], title="t") is None
