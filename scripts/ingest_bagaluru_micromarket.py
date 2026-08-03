"""
Ingest PropStack Bagaluru Micro Market Analysis workbook into AURA-Market CSVs.

Usage:
  python scripts/ingest_bagaluru_micromarket.py
  python scripts/ingest_bagaluru_micromarket.py "C:\\path\\to\\Bagaluru - Micro Market Analysis(1).xlsx"
"""
from __future__ import annotations

import math
import re
import shutil
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
RAW = DATA / "raw"
DOWNLOADS = Path(r"C:\Users\Admin\Downloads")
DEFAULT_XLSX = DOWNLOADS / "Bagaluru - Micro Market Analysis(1).xlsx"

DEVELOPER_MAP = {
    "adarsh developers": "Adarsh",
    "brigade group": "Brigade",
    "godrej properties": "Godrej",
    "kalyani developers": "Kalyani",
    "kumar properties": "Kumar",
    "mjr builders": "MJR",
    "nvg projects": "NVG",
    "puravankara & provident housing": "Puravankara",
    "sri sai dev enclave": "Sri Sai Dev",
}

BRAND_DEFAULTS = {
    "Brigade": 9.2,
    "Godrej": 9.4,
    "Kalyani": 7.5,
    "Puravankara": 8.6,
    "Adarsh": 8.0,
    "Kumar": 6.8,
    "MJR": 7.2,
    "NVG": 6.5,
    "Sri Sai Dev": 6.0,
}

# Seed lat/lon keyed by normalized developer + short name fragments
SEED_GEO: list[tuple[str, str, float, float, float]] = [
    ("Brigade", "diora", 13.149, 77.675, 9.2),
    ("Brigade", "cobalt", 13.150, 77.676, 9.2),
    ("Brigade", "beryl", 13.151, 77.677, 9.2),
    ("Brigade", "aurum", 13.142, 77.668, 9.0),
    ("Brigade", "luminaire", 13.138, 77.670, 9.0),
    ("Brigade", "emerald", 13.138, 77.670, 9.0),
    ("Godrej", "tower h", 13.155, 77.682, 9.4),
    ("Godrej", "tower p", 13.156, 77.683, 9.4),
    ("Godrej", "tower m", 13.157, 77.684, 9.4),
    ("Godrej", "tower l", 13.158, 77.685, 9.4),
    ("Godrej", "ananda", 13.155, 77.682, 9.4),
    ("Kalyani", "tower 1", 13.145, 77.690, 7.5),
    ("Kalyani", "tower 3", 13.146, 77.691, 7.5),
    ("Kalyani", "living tree", 13.145, 77.690, 7.5),
    ("Puravankara", "ecopolitan v", 13.153, 77.696, 8.6),
    ("Puravankara", "ecopolitan", 13.152, 77.695, 8.6),
    ("Adarsh", "palm", 13.140, 77.660, 8.0),
    ("Kumar", "plumeria", 13.135, 77.665, 6.8),
    ("MJR", "north park", 13.160, 77.670, 7.2),
    ("NVG", "rakshak", 13.148, 77.700, 6.5),
    ("Sri Sai Dev", "dev enclave", 13.130, 77.680, 6.0),
]

STAGE_PROGRESS = [
    (r"ready", 100),
    (r"finish", 85),
    (r"interior", 70),
    (r"pillar|slab", 45),
    (r"excavation|plinth", 15),
    (r"under construction", 50),
]


def _num(v, default: float | None = None) -> float | None:
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return default
    if isinstance(v, str):
        s = v.strip().replace(",", "")
        if s in ("", "-", "—", "N/A", "nan"):
            return default
        try:
            return float(s)
        except ValueError:
            return default
    try:
        x = float(v)
        return default if math.isnan(x) else x
    except (TypeError, ValueError):
        return default


def _to_month(v) -> str | None:
    ts = pd.to_datetime(v, errors="coerce")
    if pd.isna(ts):
        return None
    return ts.strftime("%Y-%m")


def normalize_developer(raw: str) -> str:
    key = str(raw or "").strip().lower()
    return DEVELOPER_MAP.get(key, str(raw or "").strip() or "Unknown")


def short_project_name(full: str) -> tuple[str, str]:
    """Return (display_name, tower_hint) from PropStack project name."""
    name = str(full or "").strip()
    tower = ""
    m = re.search(r"\(([^)]+)\)\s*$", name)
    if m:
        tower = m.group(1).strip()
        base = name[: m.start()].strip()
    else:
        base = name
    # Prefer shorter brand-facing labels
    aliases = [
        (r"(?i)adarsh palm acres", "Palm Acres III"),
        (r"(?i)aurum at brigade", "Aurum"),
        (r"(?i)emerald\s*&\s*luminaire", "Emerald & Luminaire"),
        (r"(?i)brigade el dorado", "El Dorado"),
        (r"(?i)godrej ananda", "Ananda III"),
        (r"(?i)kalyani living tree", "Living Tree"),
        (r"(?i)kumar plumeria", "Plumeria"),
        (r"(?i)^north park", "North Park"),
        (r"(?i)nvg rakshak", "Rakshak"),
        (r"(?i)provident ecopolitan\s*v\b", "Ecopolitan V"),
        (r"(?i)provident ecopolitan\b", "Provident Ecopolitan"),
        (r"(?i)sri sai dev enclave", "Dev Enclave"),
    ]
    display = base
    for pat, label in aliases:
        if re.search(pat, base):
            display = label
            break
    if tower:
        # Compact tower labels
        t = tower
        t = re.sub(r"(?i)tower\s*", "T", t)
        t = re.sub(r"\s+", " ", t).strip(" ,")
        display = f"{display} - {t}"
    return display, tower or "-"


def progress_from_stage(stage: str) -> float:
    s = str(stage or "").lower()
    for pat, pct in STAGE_PROGRESS:
        if re.search(pat, s):
            return float(pct)
    return 50.0


def map_status(current: str, stage: str) -> str:
    cur = str(current or "").strip().lower()
    stg = str(stage or "").lower()
    if cur == "sold":
        return "Sold Out"
    if "ready" in stg:
        return "Ready"
    if cur == "available":
        return "Under Construction"
    return str(current or "Under Construction").strip() or "Under Construction"


def map_segment(raw) -> str:
    s = str(raw or "").strip().lower()
    if s in ("luxury",):
        return "Luxury"
    if s in ("mid", "premium"):
        return "Premium"
    if s in ("value", "affordable"):
        return "Value"
    if not s or s == "nan":
        return "Value"
    return str(raw).strip().title()


def geo_for(developer: str, project: str, tower: str) -> tuple[float, float, float]:
    blob = f"{project} {tower}".lower()
    for dev, frag, lat, lon, brand in SEED_GEO:
        if dev == developer and frag in blob:
            return lat, lon, brand
    return 13.15, 77.68, BRAND_DEFAULTS.get(developer, 7.0)


def price_psf_row(r: pd.Series) -> float:
    for col in ("New Launch Price", "Sale-RS/SqftMin", "LQPrice-RS/SqftMin", "CRM_Price", "Resale-RS/SqftMin"):
        v = _num(r.get(col))
        if v and v > 0:
            # Aurum odd launch 5265 — prefer resale/LQ if launch looks like typo vs market
            if col == "New Launch Price" and v < 6000:
                for alt in ("Resale-RS/SqftMin", "LQPrice-RS/SqftMin", "Sale-RS/SqftMin"):
                    a = _num(r.get(alt))
                    if a and a > v:
                        return float(a)
            return float(v)
    return 7500.0


def avg_size_row(r: pd.Series) -> float:
    mn = _num(r.get("Unit Size-SqftMin"))
    mx = _num(r.get("Unit Size-SqftMax"))
    launched_sqft = _num(r.get("Launched Sqft"))
    units = _num(r.get("Launched Units"))
    if mn and mx and mx > 0:
        return round((mn + mx) / 2, 0)
    if mn and mn > 0:
        return float(mn)
    if launched_sqft and units and units > 0:
        return round(launched_sqft / units, 0)
    return 1200.0


def ingest_projects(path: Path) -> pd.DataFrame:
    raw = pd.read_excel(path, sheet_name="Projects List", header=1)
    raw = raw.dropna(subset=["Project Name"]).copy()
    raw = raw[~raw["Project Name"].astype(str).str.contains(r"(?i)^note:|^\*", na=False)]
    rows = []
    for _, r in raw.iterrows():
        launched = _num(r.get("Launched Units"))
        if not launched or launched <= 0:
            continue
        sold = _num(r.get("AbsorbedUnits"), 0.0) or 0.0
        sold = min(sold, launched)
        developer = normalize_developer(r.get("Developer"))
        display, tower = short_project_name(r.get("Project Name"))
        delay = _num(r.get("DelayMonths1"))
        if delay is None:
            delay = _num(r.get("DelayMonths"), 0.0) or 0.0
        lat, lon, brand = geo_for(developer, display, tower)
        abs_pct = _num(r.get("%Sold"))
        if abs_pct is None:
            abs_pct = round(sold / launched * 100, 1)
        rows.append(
            {
                "developer": developer,
                "project": display,
                "tower": tower if tower else str(r.get("Phase") or "-"),
                "total_units": int(launched),
                "units_sold": int(round(sold)),
                "price_psf": int(round(price_psf_row(r))),
                "avg_unit_size_sqft": int(round(avg_size_row(r))),
                "construction_delay_months": int(round(delay)),
                "construction_progress_pct": progress_from_stage(r.get("Construction Stage")),
                "brand_score": brand,
                "lat": lat,
                "lon": lon,
                "status": map_status(r.get("Current Status"), r.get("Construction Stage")),
                "units_unsold": int(round(launched - sold)),
                "absorption_pct": round(float(abs_pct), 1),
                "segment": map_segment(r.get("PropertySegment")),
                "micro_market": "Bagaluru / Aerospace Highway",
                "project_sub_type": str(r.get("Project Sub Type") or "").strip(),
                "rera_id": str(r.get("ReraCertificateNo") or "").strip(),
                "launch_date": r.get("Launch Date"),
                "completion_date": r.get("Completion Date"),
            }
        )
    return pd.DataFrame(rows)


def projects_to_rera(projects: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, r in projects.iterrows():
        rid = str(r.get("rera_id") or "").strip()
        if not rid or rid.lower() in ("nan", "-", "none"):
            continue
        approval = pd.to_datetime(r.get("launch_date"), errors="coerce")
        rows.append(
            {
                "rera_id": rid,
                "project": r["project"],
                "developer": r["developer"],
                "approval_date": approval.strftime("%Y-%m-%d") if pd.notna(approval) else "",
                "micro_market": "Bagaluru",
                "units": int(r["total_units"]),
                "status": "Approved",
            }
        )
    return pd.DataFrame(rows).drop_duplicates(subset=["rera_id"], keep="first")


def projects_to_under_construction(projects: pd.DataFrame) -> pd.DataFrame:
    active = projects[~projects["status"].astype(str).isin(["Sold Out"])].copy()
    rows = []
    for _, r in active.iterrows():
        comp = pd.to_datetime(r.get("completion_date"), errors="coerce")
        rows.append(
            {
                "project": r["project"],
                "developer": r["developer"],
                "total_units": int(r["total_units"]),
                "unsold_units": int(r["units_unsold"]),
                "construction_pct": float(r["construction_progress_pct"]),
                "expected_completion": comp.strftime("%Y-%m") if pd.notna(comp) else "",
                "note": str(r.get("project_sub_type") or r.get("status") or ""),
            }
        )
    return pd.DataFrame(rows)


def sheet_header_row(path: Path, sheet: str, header: int = 0) -> pd.DataFrame:
    df = pd.read_excel(path, sheet_name=sheet, header=header)
    return df


def ingest_inventory(path: Path) -> pd.DataFrame:
    df = pd.read_excel(path, sheet_name="Inventory Trend", header=None)
    # Find header row with Period
    hdr = 0
    for i in range(min(5, len(df))):
        if any(str(x).strip() == "Period" for x in df.iloc[i].tolist()):
            hdr = i
            break
    body = pd.read_excel(path, sheet_name="Inventory Trend", header=hdr)
    body.columns = [str(c).strip() for c in body.columns]
    # Drop unnamed index col
    cols = [c for c in body.columns if not c.lower().startswith("unnamed")]
    body = body[cols].copy()
    rename = {}
    for c in body.columns:
        cl = c.lower()
        if "period" in cl:
            rename[c] = "month"
        elif "absorbed" in cl:
            rename[c] = "absorbed_units"
        elif "unsold" in cl:
            rename[c] = "unsold_units"
        elif "overhang" in cl:
            rename[c] = "inventory_overhang_months"
    body = body.rename(columns=rename)
    body["month"] = body["month"].map(_to_month)
    for c in ("absorbed_units", "unsold_units", "inventory_overhang_months"):
        if c in body.columns:
            body[c] = pd.to_numeric(body[c], errors="coerce")
    return body.dropna(subset=["month"]).reset_index(drop=True)


def ingest_weighted_price(path: Path) -> pd.DataFrame:
    df = pd.read_excel(path, sheet_name="Weighted Avg Price Trend", header=0)
    df = df.rename(
        columns={
            "Period": "period",
            "Wt. Avg. Price NewLaunch (/Sqft)": "wt_avg_new_launch_psf",
            "Wt. Avg. Price Absorbed (/Sqft)": "wt_avg_absorbed_psf",
            "Wt. Avg. Price Available Units (/Sqft)": "wt_avg_available_psf",
        }
    )
    keep = [c for c in ("period", "wt_avg_new_launch_psf", "wt_avg_absorbed_psf", "wt_avg_available_psf") if c in df.columns]
    out = df[keep].copy()
    for c in keep[1:]:
        out[c] = pd.to_numeric(out[c], errors="coerce")
    return out.dropna(subset=["period"]).reset_index(drop=True)


def ingest_new_launches(path: Path) -> pd.DataFrame:
    df = pd.read_excel(path, sheet_name="New Launch Data", header=None)
    hdr = 0
    for i in range(min(5, len(df))):
        if any(str(x).strip() == "Period" for x in df.iloc[i].tolist()):
            hdr = i
            break
    body = pd.read_excel(path, sheet_name="New Launch Data", header=hdr)
    body.columns = [str(c).strip() for c in body.columns]
    cols = [c for c in body.columns if not str(c).lower().startswith("unnamed")]
    body = body[cols].copy()
    rename = {
        "Period": "month",
        "No. of Projects Launched": "projects_launched",
        "No. of Units": "units_launched",
        "Wt. Min Price (/Sqft)": "wt_min_psf",
        "Wt. Avg. Price (/Sqft)": "wt_avg_psf",
        "Wt. Max Price (/Sqft)": "wt_max_psf",
        "Absorbed Units": "absorbed_units",
    }
    body = body.rename(columns={k: v for k, v in rename.items() if k in body.columns})
    if "month" in body.columns:
        body["month"] = body["month"].map(_to_month)
    for c in body.columns:
        if c != "month":
            body[c] = pd.to_numeric(body[c], errors="coerce")
    # Keep only months with at least one launch metric
    if "units_launched" in body.columns:
        body = body.dropna(subset=["month", "units_launched"], how="any")
    else:
        body = body.dropna(subset=["month"])
    return body.reset_index(drop=True)


def ingest_productwise_supply(path: Path) -> pd.DataFrame:
    df = pd.read_excel(path, sheet_name="Productwise Supply", header=None)
    hdr = 0
    for i in range(min(5, len(df))):
        if any(str(x).strip() == "Period" for x in df.iloc[i].tolist()):
            hdr = i
            break
    body = pd.read_excel(path, sheet_name="Productwise Supply", header=hdr)
    body.columns = [str(c).strip() for c in body.columns]
    cols = [c for c in body.columns if not str(c).lower().startswith("unnamed")]
    body = body[cols].copy()
    rename = {}
    for c in body.columns:
        cl = c.lower()
        if "period" in cl:
            rename[c] = "month"
        elif "apartment" in cl:
            rename[c] = "apartment_units"
        elif "row house" in cl or "villa" in cl:
            rename[c] = "villa_units"
        elif "plot" in cl:
            rename[c] = "plot_units"
        elif "total" in cl:
            rename[c] = "total_units"
    body = body.rename(columns=rename)
    body["month"] = body["month"].map(_to_month)
    for c in ("apartment_units", "villa_units", "plot_units", "total_units"):
        if c in body.columns:
            body[c] = pd.to_numeric(body[c], errors="coerce")
    body = body.dropna(subset=["month"])
    # Keep rows with any supply
    metric_cols = [c for c in ("apartment_units", "villa_units", "plot_units", "total_units") if c in body.columns]
    if metric_cols:
        body = body.dropna(subset=metric_cols, how="all")
    return body.reset_index(drop=True)


def ingest_productwise_supply_absorption(path: Path) -> pd.DataFrame:
    """Flatten multi-header PropStack sheet into long rows."""
    raw = pd.read_excel(path, sheet_name="Productwise Supply & Absorption", header=None)
    # Row0: product groups, Row1: Supply/Absorption/Availability, Row2+: data
    # Find period column
    data_start = 2
    for i in range(min(5, len(raw))):
        if str(raw.iloc[i, 1]).strip() == "Period" or (
            i > 0 and pd.notna(raw.iloc[i, 1]) and "202" in str(raw.iloc[i, 1])
        ):
            if str(raw.iloc[i, 1]).strip() == "Period":
                data_start = i + 2  # after Period + subheader
            break
    # Use known structure from export: col1=Period, then Apt S/A/Av, Villa S/A/Av, Plot S/A/Av, Total S/A/Av
    records = []
    for i in range(data_start, len(raw)):
        period = raw.iloc[i, 1]
        month = _to_month(period)
        if not month:
            continue
        groups = [
            ("Apartment Cmplx", 2, 3, 4),
            ("Row House/Villas", 5, 6, 7),
            ("Plots", 8, 9, 10),
            ("Total", 11, 12, 13),
        ]
        for product, s_i, a_i, v_i in groups:
            supply = _num(raw.iloc[i, s_i] if s_i < raw.shape[1] else None)
            absorbed = _num(raw.iloc[i, a_i] if a_i < raw.shape[1] else None)
            available = _num(raw.iloc[i, v_i] if v_i < raw.shape[1] else None)
            if supply is None and absorbed is None and available is None:
                continue
            records.append(
                {
                    "month": month,
                    "product_type": product,
                    "supply_units": supply,
                    "absorption_units": absorbed,
                    "availability_units": available,
                }
            )
    return pd.DataFrame(records)


def ingest_cumulative(path: Path) -> pd.DataFrame:
    df = pd.read_excel(path, sheet_name="Cumulative Supply & Absorption", header=None)
    hdr = 0
    for i in range(min(5, len(df))):
        if any(str(x).strip() == "Period" for x in df.iloc[i].tolist()):
            hdr = i
            break
    body = pd.read_excel(path, sheet_name="Cumulative Supply & Absorption", header=hdr)
    body.columns = [str(c).strip() for c in body.columns]
    cols = [c for c in body.columns if not str(c).lower().startswith("unnamed")]
    body = body[cols].copy()
    rename = {
        "Period": "month",
        "Supply (Units)": "supply_units",
        "Absorption (Units)": "absorption_units",
        "Available Supply (Units)": "available_units",
        "Cumulative Supply (Units)": "cumulative_supply",
        "Cumulative Absorption (Units)": "cumulative_absorption",
        "Cumulative Availability (Units)": "cumulative_availability",
    }
    body = body.rename(columns={k: v for k, v in rename.items() if k in body.columns})
    body["month"] = body["month"].map(_to_month)
    for c in body.columns:
        if c != "month":
            body[c] = pd.to_numeric(body[c], errors="coerce")
    return body.dropna(subset=["month"]).reset_index(drop=True)


def ingest_absorption_breakup(path: Path) -> pd.DataFrame:
    df = pd.read_excel(path, sheet_name="Absorption Break-up", header=None)
    hdr = 0
    for i in range(min(5, len(df))):
        if any(str(x).strip() == "Period" for x in df.iloc[i].tolist()):
            hdr = i
            break
    body = pd.read_excel(path, sheet_name="Absorption Break-up", header=hdr)
    body.columns = [str(c).strip() for c in body.columns]
    cols = [c for c in body.columns if not str(c).lower().startswith("unnamed")]
    body = body[cols].copy()
    if "Period" in body.columns:
        body = body.rename(columns={"Period": "period"})
    id_col = "period"
    value_cols = [c for c in body.columns if c != id_col]
    long = body.melt(id_vars=[id_col], value_vars=value_cols, var_name="price_band", value_name="units")
    long["units"] = pd.to_numeric(long["units"], errors="coerce").fillna(0)
    long = long[long["price_band"].astype(str).str.lower() != "total"]
    return long.reset_index(drop=True)


def ingest_wide_quarterly(path: Path, sheet: str, value_name: str) -> pd.DataFrame:
    raw = pd.read_excel(path, sheet_name=sheet, header=None)
    # Find header row containing "Region"
    hdr = 0
    for i in range(min(6, len(raw))):
        vals = [str(x).strip() for x in raw.iloc[i].tolist()]
        if "Region" in vals:
            hdr = i
            break
    header = [str(x).strip() if pd.notna(x) else f"col_{j}" for j, x in enumerate(raw.iloc[hdr].tolist())]
    body = raw.iloc[hdr + 1 :].copy()
    body.columns = header
    # Drop fully empty / unnamed leading columns
    keep = [c for c in body.columns if c and not c.lower().startswith("col_") and c.lower() != "nan"]
    body = body[keep].copy()
    if "Region" not in body.columns:
        body = body.rename(columns={body.columns[0]: "Region"})
    # Deduplicate column names
    seen: dict[str, int] = {}
    new_cols = []
    for c in body.columns:
        if c in seen:
            seen[c] += 1
            new_cols.append(f"{c}_{seen[c]}")
        else:
            seen[c] = 0
            new_cols.append(c)
    body.columns = new_cols
    long = body.melt(id_vars=["Region"], var_name="period", value_name=value_name)
    long = long.rename(columns={"Region": "region"})
    long[value_name] = pd.to_numeric(long[value_name], errors="coerce")
    long = long.dropna(subset=[value_name])
    return long.reset_index(drop=True)


def build_summary(projects: pd.DataFrame, inventory: pd.DataFrame) -> pd.DataFrame:
    """PropStack Location Analysis snapshot (matches Summary dashboard)."""
    total_units = int(projects["total_units"].sum())
    sold = int(projects["units_sold"].sum())
    unsold = int(projects["units_unsold"].sum())
    abs_pct = round(sold / total_units * 100, 2) if total_units else 0.0
    # Parent project count: PropStack shows 12 — use unique base names before " - "
    base_names = projects["project"].astype(str).str.split(" - ").str[0].nunique()
    overhang = None
    if not inventory.empty and "inventory_overhang_months" in inventory.columns:
        overhang = float(inventory.iloc[-1]["inventory_overhang_months"])
    # Verticals from project_sub_type
    def _vert(sub: str) -> str:
        s = str(sub).lower()
        if "villa" in s or "row" in s:
            return "Row House/Villas"
        if "plot" in s:
            return "Plots"
        return "Apartment Cmplx"

    verts = projects.copy()
    verts["vertical"] = verts["project_sub_type"].map(_vert)
    vstats = verts.groupby("vertical").agg(
        supply=("total_units", "sum"),
        absorption=("units_sold", "sum"),
        availability=("units_unsold", "sum"),
        wt_price=("price_psf", "mean"),
    )
    apt = vstats.loc["Apartment Cmplx"] if "Apartment Cmplx" in vstats.index else None
    villa = vstats.loc["Row House/Villas"] if "Row House/Villas" in vstats.index else None
    plot = vstats.loc["Plots"] if "Plots" in vstats.index else None
    return pd.DataFrame(
        [
            {
                "micro_market": "Bagaluru / NorthEast Region",
                "projects": int(base_names),
                "developers": int(projects["developer"].nunique()),
                "total_units": total_units,
                "units_sold": sold,
                "units_unsold": unsold,
                "absorption_pct": abs_pct,
                "availability_pct": round(100 - abs_pct, 2),
                "inventory_overhang_months": overhang,
                "apt_supply": int(apt["supply"]) if apt is not None else 0,
                "apt_absorption": int(apt["absorption"]) if apt is not None else 0,
                "apt_availability": int(apt["availability"]) if apt is not None else 0,
                "apt_wt_avg_psf": round(float(apt["wt_price"]), 0) if apt is not None else None,
                "villa_supply": int(villa["supply"]) if villa is not None else 0,
                "villa_absorption": int(villa["absorption"]) if villa is not None else 0,
                "villa_availability": int(villa["availability"]) if villa is not None else 0,
                "villa_wt_avg_psf": round(float(villa["wt_price"]), 0) if villa is not None else None,
                "plot_supply": int(plot["supply"]) if plot is not None else 0,
                "plot_absorption": int(plot["absorption"]) if plot is not None else 0,
                "plot_availability": int(plot["availability"]) if plot is not None else 0,
                "plot_wt_avg_psf": round(float(plot["wt_price"]), 0) if plot is not None else None,
                "source": "PropStack Bagaluru export",
                "period_label": "Dec 2022 - Nov 2025",
            }
        ]
    )


def monthly_absorption_from_projects(
    projects: pd.DataFrame,
    inventory: pd.DataFrame,
) -> pd.DataFrame:
    """Synthetic project-month series calibrated to Inventory Trend market absorption."""
    rng = np.random.default_rng(42)
    if inventory.empty:
        months = pd.date_range("2023-01-01", "2025-11-01", freq="MS")
        market_abs = np.ones(len(months))
    else:
        inv = inventory.copy()
        inv["ts"] = pd.to_datetime(inv["month"] + "-01")
        months = inv["ts"]
        market_abs = inv["absorbed_units"].fillna(0).to_numpy(dtype=float)
        if market_abs.sum() <= 0:
            market_abs = np.ones(len(months))

    records = []
    for _, p in projects.iterrows():
        target = float(p["units_sold"])
        if target <= 0:
            continue
        weights = market_abs / market_abs.sum()
        noise = rng.normal(1.0, 0.08, len(months))
        noise = np.clip(noise, 0.5, 1.5)
        series = weights * noise
        series = series / series.sum() * target
        cumulative = np.cumsum(series)
        for i, m in enumerate(months):
            records.append(
                {
                    "month": pd.Timestamp(m).strftime("%Y-%m"),
                    "developer": p["developer"],
                    "project": p["project"],
                    "units_sold_month": round(float(series[i]), 2),
                    "cumulative_sold": round(float(cumulative[i]), 2),
                    "total_units": int(p["total_units"]),
                    "absorption_pct": round(float(cumulative[i] / p["total_units"] * 100), 2),
                }
            )
    return pd.DataFrame(records)


def main(argv: list[str] | None = None) -> None:
    argv = argv if argv is not None else sys.argv[1:]
    src = Path(argv[0]) if argv else DEFAULT_XLSX
    if not src.exists():
        raise SystemExit(f"Excel not found: {src}")

    DATA.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(parents=True, exist_ok=True)
    dest = RAW / "Bagaluru_Micro_Market_Analysis.xlsx"
    shutil.copy2(src, dest)
    print("Copied workbook ->", dest)

    projects = ingest_projects(src)
    # Drop helper cols not in seed schema before write (keep extras out of strict CSV)
    proj_out = projects.drop(
        columns=[c for c in ("project_sub_type", "rera_id", "launch_date", "completion_date") if c in projects.columns],
        errors="ignore",
    )
    # Keep rera/launch on full frame for derived tables
    inventory = ingest_inventory(src)
    weighted = ingest_weighted_price(src)
    launches = ingest_new_launches(src)
    product_supply = ingest_productwise_supply(src)
    product_sa = ingest_productwise_supply_absorption(src)
    cumulative = ingest_cumulative(src)
    breakup = ingest_absorption_breakup(src)
    mm_unsold = ingest_wide_quarterly(src, "Micro Market Supply & Absorptio", "unsold_units")
    mm_price = ingest_wide_quarterly(src, "Micro Market Wt Avg Price Trend", "wt_avg_psf")
    summary = build_summary(projects, inventory)
    monthly = monthly_absorption_from_projects(proj_out, inventory)
    rera = projects_to_rera(projects)
    under = projects_to_under_construction(projects)

    proj_out.to_csv(DATA / "projects.csv", index=False)
    monthly.to_csv(DATA / "monthly_absorption.csv", index=False)
    inventory.to_csv(DATA / "inventory_trend.csv", index=False)
    weighted.to_csv(DATA / "weighted_price_trend.csv", index=False)
    launches.to_csv(DATA / "new_launches.csv", index=False)
    product_supply.to_csv(DATA / "productwise_supply.csv", index=False)
    product_sa.to_csv(DATA / "productwise_supply_absorption.csv", index=False)
    cumulative.to_csv(DATA / "cumulative_supply_absorption.csv", index=False)
    breakup.to_csv(DATA / "absorption_by_price_band.csv", index=False)
    mm_unsold.to_csv(DATA / "micromarket_quarterly_unsold.csv", index=False)
    mm_price.to_csv(DATA / "micromarket_wt_price_quarterly.csv", index=False)
    summary.to_csv(DATA / "micromarket_summary.csv", index=False)
    if not rera.empty:
        rera.to_csv(DATA / "rera_projects.csv", index=False)
    if not under.empty:
        under.to_csv(DATA / "under_construction.csv", index=False)

    total = int(proj_out["total_units"].sum())
    sold = int(proj_out["units_sold"].sum())
    print(f"projects={len(proj_out)} units={total} sold={sold} abs%={round(sold/total*100,2) if total else 0}")
    print("summary row:", summary.iloc[0].to_dict())
    print("Wrote PropStack CSVs to", DATA)


if __name__ == "__main__":
    main()
