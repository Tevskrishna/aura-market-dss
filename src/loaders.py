from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


@lru_cache(maxsize=1)
def load_projects() -> pd.DataFrame:
    return pd.read_csv(DATA / "projects.csv")


@lru_cache(maxsize=1)
def load_monthly() -> pd.DataFrame:
    df = pd.read_csv(DATA / "monthly_absorption.csv")
    df["month"] = pd.to_datetime(df["month"] + "-01")
    return df


@lru_cache(maxsize=1)
def load_zones() -> pd.DataFrame:
    return pd.read_csv(DATA / "zones.csv")


@lru_cache(maxsize=1)
def load_rera() -> pd.DataFrame:
    df = pd.read_csv(DATA / "rera_projects.csv")
    df["approval_date"] = pd.to_datetime(df["approval_date"])
    return df


@lru_cache(maxsize=1)
def load_upcoming() -> pd.DataFrame:
    return pd.read_csv(DATA / "upcoming_projects.csv")


@lru_cache(maxsize=1)
def load_under_construction() -> pd.DataFrame:
    return pd.read_csv(DATA / "under_construction.csv")


@lru_cache(maxsize=1)
def load_land() -> pd.DataFrame:
    return pd.read_csv(DATA / "land_prices.csv")


@lru_cache(maxsize=1)
def load_demographics() -> pd.DataFrame:
    path = DATA / "buyer_demographics.csv"
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


@lru_cache(maxsize=1)
def load_smc() -> pd.DataFrame:
    path = DATA / "smc_spends.csv"
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


def filter_projects(developer: str | None = None) -> pd.DataFrame:
    df = load_projects()
    if developer and developer != "All Developers":
        return df[df["developer"] == developer].copy()
    return df.copy()
