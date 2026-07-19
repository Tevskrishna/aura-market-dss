"""Generate seed CSVs for Bagaluru micro-market DSS + ingest booking Excels."""
from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DOWNLOADS = Path(r"C:\Users\Admin\Downloads")
rng = np.random.default_rng(42)


def sigma_from_dpmo(dpmo: float) -> float:
    """Approximate Six Sigma level from DPMO (lookup + interpolate)."""
    table = [
        (308537, 0.5),
        (226627, 1.0),
        (158655, 1.5),
        (66807, 2.0),
        (22750, 2.5),
        (6210, 3.0),
        (1350, 3.5),
        (233, 4.0),
        (32, 4.5),
        (3.4, 5.0),
        (0.57, 5.5),
        (0.002, 6.0),
    ]
    if dpmo >= table[0][0]:
        return table[0][1]
    for i in range(len(table) - 1):
        d1, s1 = table[i]
        d2, s2 = table[i + 1]
        if d2 <= dpmo <= d1:
            t = (math.log(d1) - math.log(max(dpmo, 1e-9))) / (math.log(d1) - math.log(d2))
            return round(s1 + t * (s2 - s1), 2)
    return 6.0


def projects() -> pd.DataFrame:
    rows = [
        # developer, project, towers, units, sold, price_psf, avg_size, delay_mo, stage_pct, brand_score, lat, lon, status
        ("Brigade", "El Dorado - Diora", "Diora", 420, 420, 8600, 1450, 0, 100, 9.2, 13.149, 77.675, "Sold Out"),
        ("Brigade", "El Dorado - Cobalt", "Cobalt", 380, 361, 9345, 1520, 2, 95, 9.2, 13.150, 77.676, "Under Construction"),
        ("Brigade", "El Dorado - Beryl", "Beryl", 350, 298, 9800, 1680, 4, 78, 9.2, 13.151, 77.677, "Under Construction"),
        ("Brigade", "Aurum", "Aurum", 560, 420, 10200, 1750, 7, 62, 9.0, 13.142, 77.668, "Under Construction"),
        ("Brigade", "Emerald & Luminaire", "E&L", 480, 288, 11000, 2100, 9, 55, 9.0, 13.138, 77.670, "Under Construction"),
        ("Godrej", "Ananda III - H/K", "H-K", 640, 512, 9200, 1380, 3, 85, 9.4, 13.155, 77.682, "Under Construction"),
        ("Godrej", "Ananda III - P", "P", 320, 240, 9450, 1420, 5, 72, 9.4, 13.156, 77.683, "Under Construction"),
        ("Godrej", "Ananda III - M", "M", 280, 154, 9900, 1550, 8, 48, 9.4, 13.157, 77.684, "Under Construction"),
        ("Godrej", "Ananda III - L", "L", 300, 210, 9700, 1480, 4, 70, 9.4, 13.158, 77.685, "Under Construction"),
        ("Kalyani", "Living Tree T1-T2", "T1-T2", 220, 198, 7800, 1280, 1, 96, 7.5, 13.145, 77.690, "Under Construction"),
        ("Kalyani", "Living Tree T3-T4", "T3-T4", 240, 156, 8100, 1320, 6, 60, 7.5, 13.146, 77.691, "Under Construction"),
        ("Kalyani", "Living Tree T5-T6", "T5-T6", 260, 130, 8450, 1400, 10, 40, 7.5, 13.147, 77.692, "Under Construction"),
        ("Puravankara", "Provident Ecopolitan", "Eco", 1800, 1497, 7200, 980, 2, 90, 8.6, 13.152, 77.695, "Under Construction"),
        ("Puravankara", "Ecopolitan V", "EcoV", 640, 288, 7600, 1050, 5, 55, 8.6, 13.153, 77.696, "Under Construction"),
        ("Adarsh", "Palm Acres III", "PA3", 420, 294, 8800, 1600, 6, 65, 8.0, 13.140, 77.660, "Under Construction"),
        ("Kumar", "Plumeria", "Plu", 180, 99, 10500, 1850, 11, 35, 6.8, 13.135, 77.665, "Under Construction"),
        ("MJR", "North Park", "NP", 360, 252, 8500, 1500, 4, 75, 7.2, 13.160, 77.670, "Under Construction"),
        ("NVG", "Rakshak", "Rak", 200, 110, 6900, 1200, 8, 50, 6.5, 13.148, 77.700, "Under Construction"),
        ("Sri Sai Dev", "Dev Enclave", "DE", 140, 70, 6500, 1150, 12, 30, 6.0, 13.130, 77.680, "Under Construction"),
    ]
    cols = [
        "developer",
        "project",
        "tower",
        "total_units",
        "units_sold",
        "price_psf",
        "avg_unit_size_sqft",
        "construction_delay_months",
        "construction_progress_pct",
        "brand_score",
        "lat",
        "lon",
        "status",
    ]
    df = pd.DataFrame(rows, columns=cols)
    df["units_unsold"] = df["total_units"] - df["units_sold"]
    df["absorption_pct"] = (df["units_sold"] / df["total_units"] * 100).round(1)
    df["segment"] = np.where(df["price_psf"] >= 9500, "Luxury", np.where(df["price_psf"] >= 8000, "Premium", "Value"))
    df["micro_market"] = "Bagaluru / Aerospace Highway"
    return df


def monthly_absorption(projects_df: pd.DataFrame) -> pd.DataFrame:
    months = pd.date_range("2022-12-01", "2025-11-01", freq="MS")
    records = []
    for _, p in projects_df.iterrows():
        target = p["units_sold"]
        base = max(target / len(months), 1.0)
        season = 1 + 0.15 * np.sin(np.linspace(0, 4 * np.pi, len(months)))
        noise = rng.normal(1.0, 0.12, len(months))
        series = np.clip(base * season * noise, 0, None)
        series = series / series.sum() * target
        cumulative = np.cumsum(series)
        for i, m in enumerate(months):
            records.append(
                {
                    "month": m.strftime("%Y-%m"),
                    "developer": p["developer"],
                    "project": p["project"],
                    "units_sold_month": round(float(series[i]), 2),
                    "cumulative_sold": round(float(cumulative[i]), 2),
                    "total_units": int(p["total_units"]),
                    "absorption_pct": round(float(cumulative[i] / p["total_units"] * 100), 2),
                }
            )
    return pd.DataFrame(records)


def zones() -> pd.DataFrame:
    zone_rows = [
        ("Bagaluru / KIADB", 13.15, 77.68, 8200, 12.5, 2.1, 0.8, 4, 6, 2, 3, "Low", 72, 88),
        ("Yelahanka", 13.10, 77.60, 7800, 9.0, 1.5, 3.2, 8, 12, 5, 6, "Low", 78, 82),
        ("Devanahalli", 13.25, 77.71, 6500, 14.0, 4.5, 1.2, 3, 5, 1, 2, "Medium", 65, 79),
        ("Hebbal", 13.05, 77.59, 11500, 7.5, 0.6, 2.5, 10, 14, 6, 4, "Low", 80, 76),
        ("Thanisandra", 13.08, 77.64, 9200, 10.2, 2.8, 4.0, 6, 9, 3, 5, "Low", 74, 80),
        ("Jakkur", 13.07, 77.62, 9800, 8.8, 1.2, 3.5, 5, 8, 4, 7, "Low", 76, 81),
        ("Hennur", 13.04, 77.66, 8800, 11.0, 3.5, 5.0, 7, 10, 3, 4, "Medium", 70, 77),
        ("Kogilu", 13.12, 77.63, 7400, 10.5, 2.0, 6.0, 3, 5, 2, 2, "Low", 68, 75),
        ("Bettahalasuru", 13.17, 77.70, 6100, 13.2, 5.0, 0.5, 2, 3, 1, 1, "Medium", 60, 73),
        ("Chikkajala", 13.19, 77.66, 5800, 15.0, 6.0, 8.0, 1, 2, 0, 1, "High", 55, 62),
        ("Whitefield", 12.97, 77.75, 10500, 6.5, 0.8, 1.0, 12, 18, 8, 9, "Low", 82, 90),
        ("Electronic City", 12.84, 77.67, 7800, 5.5, 4.2, 2.0, 9, 15, 5, 6, "Medium", 71, 74),
        ("Sarjapur", 12.91, 77.78, 8200, 9.8, 5.5, 7.0, 6, 11, 3, 4, "Medium", 69, 76),
        ("Koramangala", 12.93, 77.62, 14500, 4.2, 1.0, 2.2, 15, 20, 10, 8, "Low", 85, 70),
        ("Indiranagar", 12.97, 77.64, 16000, 3.8, 0.5, 1.5, 14, 16, 9, 7, "Low", 86, 68),
        ("Banashankari", 12.92, 77.55, 9500, 5.0, 2.5, 3.0, 10, 14, 6, 8, "Low", 79, 72),
        ("RR Nagar", 12.92, 77.52, 7200, 6.0, 3.0, 4.5, 7, 10, 4, 5, "Low", 73, 71),
        ("Mysore Road", 12.95, 77.52, 6800, 7.2, 4.0, 5.5, 5, 8, 3, 3, "Medium", 66, 65),
        ("Tumkur Road", 13.05, 77.50, 7000, 8.5, 3.8, 6.5, 4, 7, 2, 3, "Medium", 64, 69),
        ("Airport Road Corridor", 13.20, 77.70, 9000, 16.0, 1.0, 0.3, 4, 6, 2, 3, "Low", 75, 85),
        ("KR Puram", 13.01, 77.70, 8600, 7.0, 0.9, 2.8, 8, 12, 4, 5, "Low", 74, 78),
        ("CV Raman Nagar", 12.98, 77.66, 10000, 5.8, 1.8, 3.2, 9, 11, 5, 4, "Low", 77, 75),
        ("Marathahalli", 12.96, 77.70, 9800, 6.2, 2.2, 1.8, 10, 13, 6, 5, "Low", 76, 79),
        ("Bellandur", 12.93, 77.67, 11000, 5.0, 3.0, 2.5, 11, 14, 7, 6, "Medium", 78, 77),
        ("Chaya Nagar / Raja Nagar proxy", 13.09, 77.61, 7600, 9.5, 2.4, 4.2, 5, 7, 2, 3, "Low", 70, 74),
    ]
    cols = [
        "zone",
        "lat",
        "lon",
        "avg_price_psf",
        "price_trend_yoy_pct",
        "metro_km",
        "highway_km",
        "hospitals",
        "schools",
        "malls",
        "parks",
        "flood_risk",
        "air_quality_index",
        "population_growth_index",
    ]
    return pd.DataFrame(zone_rows, columns=cols)


def competition_tables() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    rera = pd.DataFrame(
        [
            ("PRM/KA/RERA/1251/2021", "Brigade El Dorado", "Brigade", "2021-06-14", "Bagaluru", 1150, "Approved"),
            ("PRM/KA/RERA/1410/2022", "Godrej Ananda III", "Godrej", "2022-03-22", "Bagaluru", 1540, "Approved"),
            ("PRM/KA/RERA/1588/2022", "Provident Ecopolitan", "Puravankara", "2022-08-01", "Bagaluru", 1800, "Approved"),
            ("PRM/KA/RERA/1672/2023", "Kalyani Living Tree", "Kalyani", "2023-01-18", "Bagaluru", 720, "Approved"),
            ("PRM/KA/RERA/1740/2023", "Adarsh Palm Acres III", "Adarsh", "2023-05-09", "Bagaluru", 420, "Approved"),
            ("PRM/KA/RERA/1811/2023", "MJR North Park", "MJR", "2023-09-12", "Bagaluru", 360, "Approved"),
            ("PRM/KA/RERA/1890/2024", "NVG Rakshak", "NVG", "2024-02-20", "Bagaluru", 200, "Approved"),
            ("PRM/KA/RERA/1955/2024", "Kumar Plumeria", "Kumar", "2024-06-05", "Bagaluru", 180, "Approved"),
            ("PRM/KA/RERA/2010/2024", "Sri Sai Dev Enclave", "Sri Sai Dev", "2024-09-30", "Bagaluru", 140, "Approved"),
            ("PRM/KA/RERA/2102/2025", "Brigade Aurum Phase Ext", "Brigade", "2025-01-15", "Bagaluru", 280, "Approved"),
            ("PRM/KA/RERA/2188/2025", "Purva Atmosphere Phase", "Puravankara", "2025-04-11", "Yelahanka fringe", 560, "Approved"),
            ("PRM/KA/RERA/2250/2025", "Sobha Dream Gardens North", "Sobha", "2025-07-08", "Bagaluru", 410, "Approved"),
        ],
        columns=["rera_id", "project", "developer", "approval_date", "micro_market", "units", "status"],
    )

    upcoming = pd.DataFrame(
        [
            ("Prestige Bagaluru Towers", "Prestige", "Coming Soon", "2026-Q3", 680, 9500, "Teaser ads live; pre-launch at ~₹9,500/sqft"),
            ("Sobha Dream Gardens North", "Sobha", "Pre-Launch", "2026-Q4", 410, 9800, "RERA approved; inventory soft-booking"),
            ("Godrej Next Plot", "Godrej", "Announced", "2027-Q1", 520, 10000, "Land bank adjacent Ananda III"),
            ("Purva Eco Extension", "Puravankara", "Coming Soon", "2026-Q2", 300, 7800, "Extension of Ecopolitan catchment"),
            ("Brigade Aerospace Habitats", "Brigade", "Teaser", "2027-Q2", 450, 11000, "Highway-facing mid-luxury tower"),
        ],
        columns=["project", "developer", "stage", "expected_launch", "planned_units", "indicative_price_psf", "signal"],
    )

    under = pd.DataFrame(
        [
            ("El Dorado Cobalt/Beryl", "Brigade", 730, 121, 78, "2027-03", "Active sales"),
            ("Aurum", "Brigade", 560, 140, 62, "2027-09", "Price pressure above ₹10k"),
            ("Ananda III", "Godrej", 1540, 424, 70, "2027-06", "Strong brand pull"),
            ("Living Tree", "Kalyani", 720, 236, 55, "2028-01", "Value segment competition"),
            ("Provident Ecopolitan", "Puravankara", 1800, 303, 90, "2026-12", "High volume / channel heavy"),
            ("Ecopolitan V", "Puravankara", 640, 352, 55, "2028-03", "Newer inventory competing Eco"),
            ("Palm Acres III", "Adarsh", 420, 126, 65, "2027-11", "Mid-premium"),
            ("Plumeria", "Kumar", 180, 81, 35, "2028-06", "Luxury mismatch risk"),
            ("North Park", "MJR", 360, 108, 75, "2027-08", "Local catchment"),
            ("Rakshak", "NVG", 200, 90, 50, "2028-02", "Affordable"),
            ("Dev Enclave", "Sri Sai Dev", 140, 70, 30, "2028-09", "Smaller brand"),
        ],
        columns=["project", "developer", "total_units", "unsold_units", "construction_pct", "expected_completion", "note"],
    )

    land = pd.DataFrame(
        [
            ("Bagaluru / KIADB", 8500, 3.7, 18.5, "Rising on Aerospace Hwy demand"),
            ("Bettahalasuru", 6200, 2.7, 22.0, "Speculative industrial spillover"),
            ("Chikkajala", 4800, 2.1, 12.0, "Flood + distance discount"),
            ("Yelahanka", 11000, 4.8, 9.5, "Mature residential"),
            ("Devanahalli", 7000, 3.0, 20.0, "Airport corridor land banking"),
            ("Thanisandra", 12500, 5.4, 8.0, "Tight supply"),
            ("Kogilu", 9000, 3.9, 11.0, "Emerging catchment"),
            ("Hebbal", 18000, 7.8, 5.0, "Prime; scarce parcels"),
        ],
        columns=["micro_market", "land_price_psf", "land_price_cr_per_acre", "yoy_change_pct", "commentary"],
    )
    return rera, upcoming, under, land


def ingest_demographics() -> pd.DataFrame:
    files = {
        "Atmosphere": DOWNLOADS / "Atmosphere (bangalore) demographic data.xlsx",
        "Blubelle": DOWNLOADS / "Blubelle Demographic data.xlsx",
        "Ecopolitan": DOWNLOADS / "Ecopolitian Demographic data.xlsx",
    }
    frames = []
    for project_label, path in files.items():
        if not path.exists():
            continue
        raw = pd.read_excel(path, header=None)
        hdr = 0
        for i in range(min(5, len(raw))):
            row = raw.iloc[i].astype(str).tolist()
            if any(x == "Stage" for x in row):
                hdr = i
                break
        df = pd.read_excel(path, header=hdr).dropna(axis=1, how="all")
        df = df[df["Stage"].astype(str).str.contains("Booking", case=False, na=False)].copy()
        df["source_project"] = project_label
        keep = [
            "source_project",
            "Stage",
            "Created Date",
            "Primary Source",
            "Apartment Sub Type",
            "Apartment",
            "Postal Code",
            "City",
            "First Time Buyer",
            "1st Applicant Age",
            "1st Applicant Gender",
            "Industry",
            "Occupation-1st Applicant",
            "1st Appicant Annual Income",
            "Annual Household Income in Lakhs",
        ]
        keep = [c for c in keep if c in df.columns]
        frames.append(df[keep])
    if not frames:
        return pd.DataFrame()
    out = pd.concat(frames, ignore_index=True)
    return out


def ingest_smc() -> pd.DataFrame:
    path = DOWNLOADS / "SMC Spends Working File.xlsx"
    if not path.exists():
        return pd.DataFrame()
    df = pd.read_excel(path, sheet_name="Sheet2", header=0)
    df = df.rename(columns={df.columns[0]: "project"})
    return df


def main() -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    proj = projects()
    proj.to_csv(DATA / "projects.csv", index=False)
    monthly_absorption(proj).to_csv(DATA / "monthly_absorption.csv", index=False)
    zones().to_csv(DATA / "zones.csv", index=False)
    rera, upcoming, under, land = competition_tables()
    rera.to_csv(DATA / "rera_projects.csv", index=False)
    upcoming.to_csv(DATA / "upcoming_projects.csv", index=False)
    under.to_csv(DATA / "under_construction.csv", index=False)
    land.to_csv(DATA / "land_prices.csv", index=False)

    demo = ingest_demographics()
    if not demo.empty:
        demo.to_csv(DATA / "buyer_demographics.csv", index=False)
        print("buyer demographics", demo.shape)
    smc = ingest_smc()
    if not smc.empty:
        smc.to_csv(DATA / "smc_spends.csv", index=False)
        print("smc", smc.shape)

    # market sigma snapshot
    total = proj["total_units"].sum()
    unsold = proj["units_unsold"].sum()
    dpmo = unsold / total * 1_000_000
    print("projects", len(proj), "units", total, "unsold", unsold, "DPMO", round(dpmo), "sigma~", sigma_from_dpmo(dpmo))
    print("Wrote seed data to", DATA)


if __name__ == "__main__":
    main()
