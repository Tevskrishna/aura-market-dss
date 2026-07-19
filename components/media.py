"""Media helpers — real-estate photography embedded for Streamlit Cloud."""
from __future__ import annotations

import base64
from pathlib import Path

from config import settings


def data_uri(filename: str) -> str:
    path = settings.ASSETS_DIR / "graphics" / filename
    if not path.exists():
        return ""
    mime = "image/jpeg" if path.suffix.lower() in {".jpg", ".jpeg"} else "image/png"
    b64 = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{b64}"


def hero_paths() -> dict[str, Path]:
    g = settings.ASSETS_DIR / "graphics"
    return {
        "night": g / "hero-bengaluru-night.jpg",
        "day": g / "hero-bagaluru-day.jpg",
    }
