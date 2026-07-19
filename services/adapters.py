"""
Data source adapters — Local CSV, Hybrid live overlay, reserved pure-live.

Competition / Market / Buyer services depend on adapters, not file paths.
Enterprise: set AURA_LIVE_*_URL env vars (JSON arrays matching seed schemas).
Without URLs, hybrid == validated seed (honest mode=local/hybrid-fallback).
"""
from __future__ import annotations

import json
import urllib.error
import urllib.request
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from io import StringIO

import pandas as pd

from config import settings
from services.data_loader import load_catalog


@dataclass(frozen=True)
class AdapterMeta:
    name: str
    mode: str  # "local" | "live" | "hybrid"
    description: str
    live_layers: tuple[str, ...] = ()


class DataAdapter(ABC):
    @abstractmethod
    def meta(self) -> AdapterMeta: ...

    @abstractmethod
    def projects(self) -> pd.DataFrame: ...

    @abstractmethod
    def bookings(self) -> pd.DataFrame: ...

    @abstractmethod
    def marketing(self) -> pd.DataFrame: ...

    @abstractmethod
    def rera(self) -> pd.DataFrame: ...

    @abstractmethod
    def upcoming(self) -> pd.DataFrame: ...

    @abstractmethod
    def under_construction(self) -> pd.DataFrame: ...

    @abstractmethod
    def land_prices(self) -> pd.DataFrame: ...

    @abstractmethod
    def zones(self) -> pd.DataFrame: ...


def _fetch_json_frame(url: str, timeout: float) -> pd.DataFrame:
    """HTTP(S) JSON or local path under the project (data/live_samples/...)."""
    from pathlib import Path

    local = Path(url)
    if not local.is_absolute():
        local = settings.PROJECT_ROOT / url
    if local.exists() and local.is_file():
        return pd.read_json(local)

    req = urllib.request.Request(url, headers={"User-Agent": "AURA-Market/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read().decode("utf-8", errors="replace")
    data = json.loads(raw)
    if isinstance(data, dict) and "data" in data:
        data = data["data"]
    return pd.read_json(StringIO(json.dumps(data)))


class LocalCatalogAdapter(DataAdapter):
    """CSV catalog, optionally hydrated from SQLite when AURA_DATA_BACKEND=sqlite."""

    def __init__(self) -> None:
        if getattr(settings, "DATA_BACKEND", "csv") == "sqlite":
            from services.sqlite_store import load_catalog_from_sqlite

            self._catalog = load_catalog_from_sqlite()
        else:
            self._catalog = load_catalog()

    def meta(self) -> AdapterMeta:
        backend = getattr(settings, "DATA_BACKEND", "csv")
        return AdapterMeta(
            name="LocalCatalogAdapter",
            mode="local",
            description=f"Validated catalog via {backend} (Atmosphere, Blubelle, Ecopolitan, SMC, seed competition).",
        )

    def _get(self, key: str) -> pd.DataFrame:
        if self._catalog.has(key):
            return self._catalog.get(key)
        return pd.DataFrame()

    def projects(self) -> pd.DataFrame:
        return self._get("projects")

    def bookings(self) -> pd.DataFrame:
        return self._get("buyer_demographics")

    def marketing(self) -> pd.DataFrame:
        return self._get("marketing_spends")

    def rera(self) -> pd.DataFrame:
        return self._get("rera_projects")

    def upcoming(self) -> pd.DataFrame:
        return self._get("upcoming_projects")

    def under_construction(self) -> pd.DataFrame:
        return self._get("under_construction")

    def land_prices(self) -> pd.DataFrame:
        return self._get("land_prices")

    def zones(self) -> pd.DataFrame:
        return self._get("zones")


@dataclass
class HybridCatalogAdapter(DataAdapter):
    """
    Local catalog + optional live JSON overlays for competition layers.
    Never raises cold-start — always serves seed if live fetch fails.
    """

    _local: LocalCatalogAdapter = field(default_factory=LocalCatalogAdapter)
    _overlay: dict[str, pd.DataFrame] = field(default_factory=dict)
    _live_ok: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        timeout = float(getattr(settings, "LIVE_TIMEOUT_SEC", 8))
        mapping = {
            "rera_projects": getattr(settings, "LIVE_RERA_URL", ""),
            "upcoming_projects": getattr(settings, "LIVE_UPCOMING_URL", ""),
            "under_construction": getattr(settings, "LIVE_UC_URL", ""),
            "land_prices": getattr(settings, "LIVE_LAND_URL", ""),
        }
        for key, url in mapping.items():
            if not url:
                continue
            try:
                frame = _fetch_json_frame(url, timeout)
                if frame is not None and not frame.empty:
                    self._overlay[key] = frame
                    self._live_ok.append(key)
            except (urllib.error.URLError, TimeoutError, ValueError, json.JSONDecodeError, OSError):
                continue

    def meta(self) -> AdapterMeta:
        if self._live_ok:
            return AdapterMeta(
                name="HybridCatalogAdapter",
                mode="hybrid",
                description=f"Live overlay on {', '.join(self._live_ok)} + local catalog elsewhere.",
                live_layers=tuple(self._live_ok),
            )
        return AdapterMeta(
            name="HybridCatalogAdapter",
            mode="hybrid",
            description="No live URLs configured or fetch failed — serving validated seed CSVs (set AURA_LIVE_*_URL).",
            live_layers=(),
        )

    def _layer(self, key: str, local_fn) -> pd.DataFrame:
        if key in self._overlay and not self._overlay[key].empty:
            return self._overlay[key].copy()
        return local_fn()

    def projects(self) -> pd.DataFrame:
        return self._local.projects()

    def bookings(self) -> pd.DataFrame:
        return self._local.bookings()

    def marketing(self) -> pd.DataFrame:
        return self._local.marketing()

    def rera(self) -> pd.DataFrame:
        return self._layer("rera_projects", self._local.rera)

    def upcoming(self) -> pd.DataFrame:
        return self._layer("upcoming_projects", self._local.upcoming)

    def under_construction(self) -> pd.DataFrame:
        return self._layer("under_construction", self._local.under_construction)

    def land_prices(self) -> pd.DataFrame:
        return self._layer("land_prices", self._local.land_prices)

    def zones(self) -> pd.DataFrame:
        return self._local.zones()


class LiveApiAdapter(HybridCatalogAdapter):
    """
    Enterprise live mode — same hybrid fetcher, but meta insists on live.
    Requires at least one successful live layer; otherwise falls back honestly.
    """

    def meta(self) -> AdapterMeta:
        base = super().meta()
        if base.live_layers:
            return AdapterMeta(
                name="LiveApiAdapter",
                mode="live",
                description=base.description,
                live_layers=base.live_layers,
            )
        return AdapterMeta(
            name="LiveApiAdapter",
            mode="live-fallback",
            description="Live mode requested but no AURA_LIVE_*_URL succeeded — seed fallback active.",
            live_layers=(),
        )


def get_adapter(mode: str | None = None) -> DataAdapter:
    mode = (mode or getattr(settings, "DATA_ADAPTER_MODE", "hybrid")).lower()
    if mode == "live":
        return LiveApiAdapter()
    if mode == "local":
        return LocalCatalogAdapter()
    return HybridCatalogAdapter()
