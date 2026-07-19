"""
Central data loading service.

Why: Every module must read the same cleaned frames through one API so
Competition / DMAIC / Buyer / Twin never re-implement CSV parsing.

Output: DataCatalog of DataFrames + ValidationReport.
Dependencies: config.settings, config.schemas, services.data_validator
"""
from __future__ import annotations

from dataclasses import dataclass, field
from functools import lru_cache

import pandas as pd

from config import settings
from config.schemas import OPTIONAL_DATASETS, REQUIRED_COLUMNS
from models.market import DatasetStatus, ValidationReport
from services.data_validator import validate_dataframe


@dataclass
class DataCatalog:
    """Shared, immutable-ish warehouse for the session."""

    frames: dict[str, pd.DataFrame] = field(default_factory=dict)
    report: ValidationReport | None = None

    def get(self, name: str) -> pd.DataFrame:
        if name not in self.frames:
            raise KeyError(f"Dataset '{name}' not loaded. Available: {list(self.frames)}")
        return self.frames[name].copy()

    def has(self, name: str) -> bool:
        return name in self.frames and not self.frames[name].empty


def _read_csv(name: str) -> tuple[pd.DataFrame | None, DatasetStatus]:
    filename = settings.DATASETS.get(name)
    if not filename:
        return None, DatasetStatus(name=name, ok=False, rows=0, path="", errors=("Unknown dataset key",))
    path = settings.DATA_DIR / filename
    if not path.exists():
        optional = name in OPTIONAL_DATASETS
        err = () if optional else (f"Missing file: {path}",)
        warn = (f"Optional dataset missing: {path}",) if optional else ()
        return None, DatasetStatus(name=name, ok=optional, rows=0, path=str(path), errors=err, warnings=warn)
    try:
        df = pd.read_csv(path)
    except Exception as exc:  # noqa: BLE001 — surface as validation error
        return None, DatasetStatus(name=name, ok=False, rows=0, path=str(path), errors=(str(exc),))
    return df, DatasetStatus(name=name, ok=True, rows=len(df), path=str(path))


def _clean_projects(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["developer"] = out["developer"].astype(str).str.strip()
    out["project"] = out["project"].astype(str).str.strip()
    for col in ["total_units", "units_sold", "units_unsold", "price_psf", "avg_unit_size_sqft"]:
        if col in out.columns:
            out[col] = pd.to_numeric(out[col], errors="coerce")
    out = out.dropna(subset=["developer", "project", "total_units"])
    out["units_unsold"] = out["units_unsold"].fillna(out["total_units"] - out["units_sold"])
    out["absorption_pct"] = (out["units_sold"] / out["total_units"] * 100).round(2)
    out["sales_value_cr"] = (
        out["units_sold"] * out["avg_unit_size_sqft"] * out["price_psf"] / 1e7
    ).round(2)
    return out


def _clean_monthly(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["month"] = pd.to_datetime(out["month"].astype(str) + "-01", errors="coerce")
    out = out.dropna(subset=["month", "project"])
    out["units_sold_month"] = pd.to_numeric(out["units_sold_month"], errors="coerce").fillna(0)
    out["developer"] = out["developer"].astype(str).str.strip()
    out["project"] = out["project"].astype(str).str.strip()
    out["fy_quarter"] = out["month"].map(_to_fy_quarter)
    return out


def _to_fy_quarter(ts: pd.Timestamp) -> str:
    """Indian FY: Apr–Mar. Q1=Apr-Jun … Q4=Jan-Mar. Label uses FY start year."""
    if pd.isna(ts):
        return ""
    month = int(ts.month)
    year = int(ts.year)
    if month >= settings.FY_START_MONTH:
        fy = year % 100
        q = (month - settings.FY_START_MONTH) // 3 + 1
    else:
        fy = (year - 1) % 100
        q = 4
    return f"FY {fy:02d}-Q{q}"


def _clean_bookings(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out = out[out["Stage"].astype(str).str.contains("Booking", case=False, na=False)].copy()
    out["Created Date"] = pd.to_datetime(out["Created Date"], dayfirst=True, errors="coerce")
    out = out.dropna(subset=["Created Date"])
    out["source_project"] = out["source_project"].astype(str).str.strip()
    out["developer"] = out["source_project"].map(settings.BOOKING_PROJECT_DEVELOPER).fillna("Unknown")
    out["project"] = out["source_project"]
    out["Apartment Sub Type"] = out["Apartment Sub Type"].fillna("Unknown").astype(str)
    out["Primary Source"] = out["Primary Source"].fillna("Unknown").astype(str)
    out["fy_quarter"] = out["Created Date"].map(_to_fy_quarter)
    return out


def _clean_marketing(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["period_start"] = pd.to_datetime(out["period_start"], errors="coerce")
    out["spend_cr"] = pd.to_numeric(out["spend_cr"], errors="coerce").fillna(0.0)
    out["project"] = out["project"].astype(str).str.strip()
    out["fy_quarter"] = out.apply(
        lambda r: f"{r['fy_label']}-Q{int(r['quarter'])}" if pd.notna(r.get("quarter")) else r.get("fy_label"),
        axis=1,
    )
    # Normalize fy_quarter to match monthly (FY YY-Qn)
    out["fy_quarter"] = out["fy_label"].astype(str) + "-Q" + out["quarter"].astype(int).astype(str)
    return out.dropna(subset=["period_start"])


_CLEANERS = {
    "projects": _clean_projects,
    "monthly_absorption": _clean_monthly,
    "buyer_demographics": _clean_bookings,
    "marketing_spends": _clean_marketing,
}


@lru_cache(maxsize=1)
def load_catalog() -> DataCatalog:
    """Load, validate, and clean all registered datasets once per process."""
    frames: dict[str, pd.DataFrame] = {}
    statuses: list[DatasetStatus] = []

    for name in settings.DATASETS:
        raw, status = _read_csv(name)
        if raw is None:
            statuses.append(status)
            continue

        required = REQUIRED_COLUMNS.get(name)
        if required:
            v_errors, v_warnings = validate_dataframe(raw, required)
            if v_errors:
                statuses.append(
                    DatasetStatus(
                        name=name,
                        ok=False,
                        rows=len(raw),
                        path=status.path,
                        errors=tuple(v_errors),
                        warnings=tuple(v_warnings),
                    )
                )
                continue
            if v_warnings:
                status = DatasetStatus(
                    name=status.name,
                    ok=True,
                    rows=status.rows,
                    path=status.path,
                    warnings=tuple(v_warnings),
                )

        cleaner = _CLEANERS.get(name)
        cleaned = cleaner(raw) if cleaner else raw.copy()
        frames[name] = cleaned
        statuses.append(
            DatasetStatus(
                name=name,
                ok=True,
                rows=len(cleaned),
                path=status.path,
                warnings=status.warnings,
            )
        )

    core_ok = all(
        any(s.name == n and s.ok for s in statuses)
        for n in ("projects", "monthly_absorption", "buyer_demographics")
    )
    report = ValidationReport(datasets=tuple(statuses), ready_for_market_overview=core_ok)
    return DataCatalog(frames=frames, report=report)


def clear_catalog_cache() -> None:
    load_catalog.cache_clear()
