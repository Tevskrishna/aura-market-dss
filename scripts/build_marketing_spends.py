"""
Normalize SMC Spends Working File → marketing_spends.csv (long format ₹ Cr).

Run: python scripts/build_marketing_spends.py
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SRC = Path(r"C:\Users\Admin\Downloads\SMC Spends Working File.xlsx")
OUT = ROOT / "data" / "marketing_spends.csv"


def main() -> None:
    raw = pd.read_excel(SRC, sheet_name="Sheet1", header=None)
    # Row0: FY labels spanning 4 cols; Row1: Q1..Q4 repeating; Row2+: project, metric, values
    fy_row = raw.iloc[0].tolist()
    q_row = raw.iloc[1].tolist()

    # Build column metadata from index 2 onward
    meta = []
    current_fy = None
    for idx in range(2, raw.shape[1]):
        fy_cell = fy_row[idx]
        q_cell = q_row[idx]
        if isinstance(fy_cell, str) and fy_cell.strip():
            # e.g. "FY 18-19" → label FY 18
            parts = fy_cell.replace("FY", "").strip().split("-")
            current_fy = f"FY {parts[0].strip()[-2:].zfill(2)}"
        q = None
        if isinstance(q_cell, str) and q_cell.strip().startswith("Q"):
            q = int(q_cell.strip().replace("Q", ""))
        meta.append((idx, current_fy, q))

    records = []
    for r in range(2, len(raw)):
        project = raw.iloc[r, 0]
        if pd.isna(project) or not str(project).strip():
            continue
        project = str(project).strip()
        for col_idx, fy_label, q in meta:
            if fy_label is None or q is None:
                continue
            val = raw.iloc[r, col_idx]
            if pd.isna(val):
                continue
            try:
                spend = float(val)
            except (TypeError, ValueError):
                continue
            # FY label year = start year of FY; Q1 starts April of that calendar year
            fy_start_year = 2000 + int(fy_label.split()[1])
            month = {1: 4, 2: 7, 3: 10, 4: 1}[q]
            year = fy_start_year if q < 4 else fy_start_year + 1
            period_start = pd.Timestamp(year=year, month=month, day=1)
            records.append(
                {
                    "project": project,
                    "fy_label": fy_label,
                    "quarter": q,
                    "period_start": period_start.strftime("%Y-%m-%d"),
                    "spend_cr": round(spend, 4),
                }
            )

    out = pd.DataFrame(records)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT, index=False)
    print(f"Wrote {len(out)} rows -> {OUT}")


if __name__ == "__main__":
    main()
