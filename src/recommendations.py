from __future__ import annotations

import pandas as pd

from src.sigma_utils import augment_for_ml


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
        causes.append("Early construction stage — trust gap for end-users")
    if row["brand_score"] < 7:
        causes.append("Weaker developer brand / financing confidence")
    if not causes:
        causes.append("No major defect signals — monitor absorption monthly")
    return causes


def recommendations_for_row(row: pd.Series, sold_out: pd.DataFrame) -> list[dict]:
    benches = sold_out if not sold_out.empty else pd.DataFrame()
    refs = ""
    if not benches.empty:
        r = benches.iloc[0]
        refs = f"Benchmark: {r['developer']} {r['project']} absorbed {r['absorption_pct']}% at ₹{int(r['price_psf']):,}/sqft"

    recs = []
    if row["price_psf"] > 9500:
        delta = row["price_psf"] - 9000
        recover = max(int(row["units_unsold"] * 0.25), 1)
        recs.append(
            {
                "issue": "High price (>₹9,500/sqft)",
                "action": "Price reduction + subvention scheme",
                "detail": f"Target ~₹8,600–9,345/sqft corridor. {refs}",
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


def fit_gb_forecast(projects: pd.DataFrame):
    """Gradient Boosting absorption forecast vs actual."""
    from sklearn.ensemble import GradientBoostingRegressor
    from sklearn.model_selection import train_test_split

    aug = augment_for_ml(projects)
    features = [
        "price_psf",
        "avg_unit_size_sqft",
        "construction_delay_months",
        "construction_progress_pct",
        "brand_score",
        "total_units",
    ]
    X = aug[features]
    y = aug["absorption_pct"]
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.25, random_state=42)
    model = GradientBoostingRegressor(random_state=42)
    model.fit(Xtr, ytr)
    preds = model.predict(projects[features])
    score = float(model.score(Xte, yte))
    out = projects[["developer", "project", "absorption_pct"]].copy()
    out["ml_forecast_pct"] = preds.round(1)
    out["gap_pp"] = (out["ml_forecast_pct"] - out["absorption_pct"]).round(1)
    return out, score, model
