"""
Thin data access wrappers — adapters stay the runtime source of frames.
Repositories exist so Wave 2 (Postgres) can swap behind the same call sites.
"""

from repositories.catalog_repo import CatalogRepository, get_catalog_repository

__all__ = ["CatalogRepository", "get_catalog_repository"]
