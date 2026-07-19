from __future__ import annotations

import hashlib

import pandas as pd

from config import settings
from services.sigma_service import augment_for_ml

_GB_FEATURES = [
    "price_psf",
    "avg_unit_size_sqft",
    "construction_delay_months",
    "construction_progress_pct",
    "brand_score",
    "total_units",
]
_ARTIFACT_DIR = settings.PROJECT_ROOT / "models" / "artifacts"
_GB_PATH = _ARTIFACT_DIR / "gb_absorption.joblib"
_HASH_PATH = _ARTIFACT_DIR / "gb_absorption.hash"


def _projects_fingerprint(projects: pd.DataFrame) -> str:
    cols = [c for c in _GB_FEATURES + ["absorption_pct", "project"] if c in projects.columns]
    payload = projects[cols].sort_values("project" if "project" in cols else cols[0]).to_csv(index=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def defect_probability(row: pd.Series) -> float:
    """Heuristic ML-like defect probability before full model fit."""
    score = 0.15
    if row["price_psf"] > 9500:
        score += 0.22
    if row["construction_delay_months"] > 6:
        score += 0.18
    if row["avg_unit_size_sqft"] > 2000:
        score += 0.12
    if row["construction_progress_pct"] < 50:
        score += 0.12
    if row["brand_score"] < 7:
        score += 0.15
    if row["absorption_pct"] < 70:
        score += 0.15
    return round(min(score, 0.95), 2)


def root_causes(row: pd.Series) -> list[str]:
    causes = []
    if row["price_psf"] > 9500:
        causes.append("High price vs Bagaluru corridor benchmarks")
    if row["construction_delay_months"] > 6:
        causes.append(f"Construction delay ({int(row['construction_delay_months'])} months)")
    if row["avg_unit_size_sqft"] > 2000:
        causes.append("Large unit size reduces affordability pool")
    if row.get("segment") == "Luxury" and row["absorption_pct"] < 80:
        causes.append("Luxury segment mismatch for micro-market demand")
    if row["construction_progress_pct"] < 50:
        causes.append("Early construction stage â€” trust gap for end-users")
    if row["brand_score"] < 7:
        causes.append("Weaker developer brand / financing confidence")
    if not causes:
        causes.append("No major defect signals â€” monitor absorption monthly")
    return causes


def recommendations_for_row(row: pd.Series, sold_out: pd.DataFrame) -> list[dict]:
    benches = sold_out if not sold_out.empty else pd.DataFrame()
    refs = ""
    if not benches.empty:
        r = benches.iloc[0]
        refs = f"Benchmark: {r['developer']} {r['project']} absorbed {r['absorption_pct']}% at â‚¹{int(r['price_psf']):,}/sqft"

    recs = []
    if row["price_psf"] > 9500:
        delta = row["price_psf"] - 9000
        recover = max(int(row["units_unsold"] * 0.25), 1)
        recs.append(
            {
                "issue": "High price (>â‚¹9,500/sqft)",
                "action": "Price reduction + subvention scheme",
                "detail": f"Target ~â‚¹8,600â€“9,345/sqft corridor. {refs}",
                "recoverable_units": recover,
                "price_cut_psf": round(delta * 0.6, 0),
            }
        )
    if row["construction_delay_months"] > 6:
        recs.append(
            {
                "issue": "Construction delay (>6 months)",
                "action": "Fast-track critical path + weekly customer updates",
                "detail": "Publish revised milestones; tie CRM updates to delay recovery.",
                "recoverable_units": max(int(row["units_unsold"] * 0.15), 1),
                "price_cut_psf": 0,
            }
        )
    if row["avg_unit_size_sqft"] > 2000:
        recs.append(
            {
                "issue": "Large unit size (>2,000 sqft)",
                "action": "Floor-plan redesign / smart 3BHK variants",
                "detail": "Shrink ticket size toward corridor median demand (Ecopolitan / Atmosphere mix).",
                "recoverable_units": max(int(row["units_unsold"] * 0.12), 1),
                "price_cut_psf": 0,
            }
        )
    if row.get("segment") == "Luxury" and row["absorption_pct"] < 80:
        recs.append(
            {
                "issue": "Luxury segment mismatch",
                "action": "NRI / investor repositioning campaign",
                "detail": "Pivot messaging from end-user to yield + airport corridor narrative.",
                "recoverable_units": max(int(row["units_unsold"] * 0.1), 1),
                "price_cut_psf": 0,
            }
        )
    if row["construction_progress_pct"] < 50:
        recs.append(
            {
                "issue": "Early construction stage",
                "action": "Virtual tours + live webcam + show flat",
                "detail": "Reduce uncertainty for first-time buyers (majority in booking samples).",
                "recoverable_units": max(int(row["units_unsold"] * 0.08), 1),
                "price_cut_psf": 0,
            }
        )
    if row["brand_score"] < 7:
        recs.append(
            {
                "issue": "Weak developer brand signal",
                "action": "CRISIL rating highlight + bank tie-up",
                "detail": "Bank pre-approvals and rating badges on all ads.",
                "recoverable_units": max(int(row["units_unsold"] * 0.1), 1),
                "price_cut_psf": 0,
            }
        )
    if not recs:
        recs.append(
            {
                "issue": "Healthy absorption",
                "action": "Hold price; pace construction communications",
                "detail": refs or "Maintain current playbook.",
                "recoverable_units": 0,
                "price_cut_psf": 0,
            }
        )
    return recs


def fit_gb_forecast(projects: pd.DataFrame, *, force_retrain: bool = False):
    """
    Gradient Boosting absorption forecast vs actual.
    Persists artifact under models/artifacts/ so UI does not retrain every click.
    """
    import joblib
    from sklearn.ensemble import GradientBoostingRegressor
    from sklearn.model_selection import train_test_split

    features = _GB_FEATURES
    fp = _projects_fingerprint(projects)
    model = None
    score = None
    loaded = False

    if not force_retrain and _GB_PATH.exists() and _HASH_PATH.exists():
        try:
            if _HASH_PATH.read_text(encoding="utf-8").strip() == fp:
                blob = joblib.load(_GB_PATH)
                model = blob["model"]
                score = float(blob.get("score", 0.0))
                loaded = True
        except Exception:
            loaded = False

    if not loaded:
        aug = augment_for_ml(projects)
        X = aug[features]
        y = aug["absorption_pct"]
        Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.25, random_state=42)
        model = GradientBoostingRegressor(random_state=42)
        model.fit(Xtr, ytr)
        score = float(model.score(Xte, yte))
        _ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
        joblib.dump({"model": model, "score": score, "features": features}, _GB_PATH)
        _HASH_PATH.write_text(fp, encoding="utf-8")

    preds = model.predict(projects[features])
    out = projects[["developer", "project", "absorption_pct"]].copy()
    out["ml_forecast_pct"] = preds.round(1)
    out["gap_pp"] = (out["ml_forecast_pct"] - out["absorption_pct"]).round(1)
    out.attrs["model_loaded_from_disk"] = loaded
    return out, score, model


def gb_artifact_status() -> dict:
    """Diagnostic for Recommendations UI."""
    return {
        "artifact_exists": _GB_PATH.exists(),
        "path": str(_GB_PATH.relative_to(settings.PROJECT_ROOT)) if _GB_PATH.exists() else "",
        "hash_path": str(_HASH_PATH.relative_to(settings.PROJECT_ROOT)) if _HASH_PATH.exists() else "",
    }

