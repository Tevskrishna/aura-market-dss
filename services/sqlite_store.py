"""
SQLite mirror of the CSV catalog — enterprise persistence step without rewriting services.

Sync: CSV/Excel load_catalog → tables in data/aura_catalog.sqlite
Read: when AURA_DATA_BACKEND=sqlite, LocalCatalogAdapter can hydrate from SQLite.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd

from config import settings
from services.data_loader import DataCatalog, clear_catalog_cache, load_catalog


def sync_catalog_to_sqlite(path: Path | None = None) -> Path:
    """Write every loaded frame to SQLite (replace). Idempotent."""
    target = path or settings.SQLITE_PATH
    target.parent.mkdir(parents=True, exist_ok=True)
    clear_catalog_cache()
    catalog = load_catalog()
    with sqlite3.connect(target) as conn:
        for name, frame in catalog.frames.items():
            if frame is None or frame.empty:
                continue
            frame.to_sql(name, conn, if_exists="replace", index=False)
        conn.execute(
            "CREATE TABLE IF NOT EXISTS _meta (k TEXT PRIMARY KEY, v TEXT)"
        )
        conn.execute(
            "INSERT OR REPLACE INTO _meta(k, v) VALUES (?, ?)",
            ("source", "csv_sync"),
        )
    return target


def load_catalog_from_sqlite(path: Path | None = None) -> DataCatalog:
    """Rebuild DataCatalog from SQLite tables."""
    target = path or settings.SQLITE_PATH
    if not target.exists():
        sync_catalog_to_sqlite(target)
    frames: dict[str, pd.DataFrame] = {}
    with sqlite3.connect(target) as conn:
        tables = pd.read_sql(
            "SELECT name FROM sqlite_master WHERE type='table' AND name != '_meta'",
            conn,
        )
        for name in tables["name"].tolist():
            frames[name] = pd.read_sql(f'SELECT * FROM "{name}"', conn)
    return DataCatalog(frames=frames, report=None)


def ensure_sqlite() -> Path:
    """Ensure mirror exists and is fresher than optional missing state."""
    path = settings.SQLITE_PATH
    if not path.exists():
        return sync_catalog_to_sqlite(path)
    return path
