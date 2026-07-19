"""
Catalog repository — wraps existing data_loader + adapter (no duplicate loading).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import pandas as pd

from services.adapters import AdapterMeta, get_adapter
from services.data_loader import DataCatalog, load_catalog


class CatalogRepository(Protocol):
    def catalog(self) -> DataCatalog: ...

    def adapter(self): ...

    def projects(self) -> pd.DataFrame: ...

    def land_prices(self) -> pd.DataFrame: ...

    def meta(self) -> AdapterMeta: ...


@dataclass
class CsvCatalogRepository:
    """Default implementation over CSV seed data via load_catalog / get_adapter."""

    def catalog(self) -> DataCatalog:
        return load_catalog()

    def adapter(self):
        return get_adapter()

    def projects(self) -> pd.DataFrame:
        return self.adapter().projects()

    def land_prices(self) -> pd.DataFrame:
        return self.adapter().land_prices()

    def meta(self) -> AdapterMeta:
        return self.adapter().meta()


def get_catalog_repository() -> CatalogRepository:
    return CsvCatalogRepository()
