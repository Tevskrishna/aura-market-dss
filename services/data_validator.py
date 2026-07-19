"""Schema validation helpers — no I/O."""
from __future__ import annotations

import pandas as pd


def validate_dataframe(df: pd.DataFrame, required_columns: list[str]) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    missing = [c for c in required_columns if c not in df.columns]
    if missing:
        errors.append(f"Missing required columns: {missing}")
    if df.empty:
        warnings.append("Dataset is empty after load")
    # duplicate column names
    if df.columns.duplicated().any():
        errors.append("Duplicate column names detected")
    return errors, warnings
