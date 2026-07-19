"""
Data source adapters — Local CSV/Excel today, live APIs tomorrow.

Competition / Market / Buyer services depend on adapters, not file paths.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

import pandas as pd

from config import settings
from services.data_loader import load_catalog


@dataclass(frozen=True)
class AdapterMeta:
    name: str
    mode: str  # "local" | "live"
    description: str


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


class LocalCatalogAdapter(DataAdapter):
    """Default production path until live KRERA / listings credentials exist."""

    def __init__(self) -> None:
        self._catalog = load_catalog()

    def meta(self) -> AdapterMeta:
        return AdapterMeta(
            name="LocalCatalogAdapter",
            mode="local",
            description="Validated Excel/CSV catalog (Atmosphere, Blubelle, Ecopolitan, SMC, seed competition).",
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


class LiveApiAdapter(DataAdapter):
    """
    Stub for live feeds (KRERA, listings, land registries).
    Raises until endpoints + credentials are configured in settings.
    """

    def meta(self) -> AdapterMeta:
        return AdapterMeta(
            name="LiveApiAdapter",
            mode="live",
            description="Reserved for live RERA / listings / land APIs.",
        )

    def _blocked(self):
        raise NotImplementedError(
            "LiveApiAdapter is not configured. Set live endpoints in config and implement fetchers."
        )

    def projects(self) -> pd.DataFrame:
        self._blocked()

    def bookings(self) -> pd.DataFrame:
        self._blocked()

    def marketing(self) -> pd.DataFrame:
        self._blocked()

    def rera(self) -> pd.DataFrame:
        self._blocked()

    def upcoming(self) -> pd.DataFrame:
        self._blocked()

    def under_construction(self) -> pd.DataFrame:
        self._blocked()

    def land_prices(self) -> pd.DataFrame:
        self._blocked()

    def zones(self) -> pd.DataFrame:
        self._blocked()


def get_adapter(mode: str | None = None) -> DataAdapter:
    mode = (mode or getattr(settings, "DATA_ADAPTER_MODE", "local")).lower()
    if mode == "live":
        return LiveApiAdapter()
    return LocalCatalogAdapter()
