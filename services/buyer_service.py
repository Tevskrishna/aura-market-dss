"""Buyer / Lead & Audience Demographics — AURA-Market MEASURE layer."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from config import settings
from models.market import FilterState
from services.adapters import get_adapter
from services.data_loader import load_catalog
from services.filter_service import apply_filters


@dataclass(frozen=True)
class BuyerInsights:
    total_bookings: int
    channel_mix: pd.DataFrame
    unit_mix: pd.DataFrame
    industry_mix: pd.DataFrame
    top_pins: pd.DataFrame
    project_split: pd.DataFrame
    age_profile: pd.DataFrame
    native_mix: pd.DataFrame
    family_mix: pd.DataFrame
    first_time_mix: pd.DataFrame


def _parse_age(val) -> float | None:
    if pd.isna(val):
        return None
    s = str(val).strip().lower().replace("years", "").replace("year", "").strip()
    try:
        return float(s)
    except ValueError:
        digits = "".join(ch for ch in s if ch.isdigit() or ch == ".")
        try:
            return float(digits) if digits else None
        except ValueError:
            return None


def _is_native_city(city: str) -> bool:
    c = str(city).strip().lower()
    if not c or c == "nan":
        return False
    return any(tok in c for tok in settings.NATIVE_CITY_TOKENS)


def _enrich(bookings: pd.DataFrame) -> pd.DataFrame:
    out = bookings.copy()
    if "1st Applicant Age" in out.columns:
        out["age"] = out["1st Applicant Age"].map(_parse_age)
        out["age_band"] = pd.cut(
            out["age"],
            bins=[0, 30, 40, 50, 60, 120],
            labels=["<=30", "31-40", "41-50", "51-60", "60+"],
        )
    else:
        out["age"] = np.nan
        out["age_band"] = "Unknown"

    if "City" in out.columns:
        out["audience_origin"] = out["City"].map(
            lambda x: "Native / Karnataka-local" if _is_native_city(x) else (
                "Unknown" if pd.isna(x) or str(x).strip() == "" else "Non-native / Outstation"
            )
        )
    else:
        out["audience_origin"] = "Unknown"

    marital_col = "Marital Status- 1st Applicant" if "Marital Status- 1st Applicant" in out.columns else None
    second = "2nd Applicant Age" if "2nd Applicant Age" in out.columns else None
    if marital_col or second:
        def _family(row):
            has_second = second and pd.notna(row.get(second))
            married = False
            if marital_col and pd.notna(row.get(marital_col)):
                married = "marri" in str(row.get(marital_col)).lower()
            if has_second or married:
                return "Family / Couple"
            return "Single / Individual"
        out["family_type"] = out.apply(_family, axis=1)
    else:
        out["family_type"] = "Unknown"

    if "First Time Buyer" in out.columns:
        out["buyer_tenure"] = out["First Time Buyer"].fillna("Unknown").astype(str)
    else:
        out["buyer_tenure"] = "Unknown"
    return out


def build_buyer_insights(filters: FilterState | None = None) -> BuyerInsights:
    if filters is not None:
        frames = apply_filters(load_catalog(), filters)
        bookings = frames["bookings"]
    else:
        bookings = get_adapter().bookings()

    empty = pd.DataFrame()
    if bookings.empty:
        return BuyerInsights(0, empty, empty, empty, empty, empty, empty, empty, empty, empty)

    bookings = _enrich(bookings)
    channel = bookings["Primary Source"].value_counts().rename_axis("channel").reset_index(name="count")
    unit = bookings["Apartment Sub Type"].value_counts().rename_axis("unit").reset_index(name="count")
    industry = (
        bookings["Industry"].fillna("Unknown").value_counts().rename_axis("industry").reset_index(name="count")
        if "Industry" in bookings.columns
        else empty
    )
    pins = empty
    if "Postal Code" in bookings.columns:
        pins = (
            bookings["Postal Code"]
            .dropna()
            .astype(str)
            .str.replace(r"\.0$", "", regex=True)
            .value_counts()
            .head(15)
            .rename_axis("postal_code")
            .reset_index(name="buyers")
        )
    split = bookings.groupby("source_project").size().rename_axis("project").reset_index(name="bookings")
    age_profile = (
        bookings["age_band"].astype(str).value_counts().rename_axis("age_band").reset_index(name="count")
    )
    native_mix = (
        bookings["audience_origin"].value_counts().rename_axis("origin").reset_index(name="count")
    )
    family_mix = (
        bookings["family_type"].value_counts().rename_axis("family_type").reset_index(name="count")
    )
    first_time = (
        bookings["buyer_tenure"].value_counts().rename_axis("buyer_tenure").reset_index(name="count")
    )
    return BuyerInsights(
        len(bookings),
        channel,
        unit,
        industry,
        pins,
        split,
        age_profile,
        native_mix,
        family_mix,
        first_time,
    )
