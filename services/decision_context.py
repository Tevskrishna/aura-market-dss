"""
CEO morning-loop decision context — session bag only, no scoring.

Hub writes after evaluate_launch; Twin / Recs / Reports read to continue
the same open decision without re-keying.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

CONTEXT_KEY = "iq_decision_context"

# Required shape keys (extras allowed)
CONTEXT_FIELDS = (
    "project",
    "my_price_psf",
    "cut_pct",
    "subvention",
    "rival_month",
    "intervene_month",
    "horizon_months",
    "verdict",
    "threat_score",
    "blind_spot_loss_cr",
    "recovery_cr",
    "updated_at",
)


def save_decision_context(
    *,
    project: str,
    my_price_psf: float,
    cut_pct: float,
    subvention: bool,
    rival_month: int,
    intervene_month: int,
    horizon_months: int,
    verdict: str,
    threat_score: int,
    blind_spot_loss_cr: float,
    recovery_cr: float,
    session: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Persist Hub open decision. Pass ``session`` in tests; otherwise Streamlit session_state."""
    bag = _session(session)
    payload: dict[str, Any] = {
        "project": str(project),
        "my_price_psf": float(my_price_psf),
        "cut_pct": float(cut_pct),
        "subvention": bool(subvention),
        "rival_month": int(rival_month),
        "intervene_month": int(intervene_month),
        "horizon_months": int(horizon_months),
        "verdict": str(verdict),
        "threat_score": int(threat_score),
        "blind_spot_loss_cr": float(blind_spot_loss_cr),
        "recovery_cr": float(recovery_cr),
        "updated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    bag[CONTEXT_KEY] = payload
    return payload


def get_decision_context(session: dict[str, Any] | None = None) -> dict[str, Any] | None:
    bag = _session(session)
    raw = bag.get(CONTEXT_KEY)
    if not isinstance(raw, dict) or not raw.get("project"):
        return None
    return dict(raw)


def has_decision_context(session: dict[str, Any] | None = None) -> bool:
    return get_decision_context(session) is not None


def clear_decision_context(session: dict[str, Any] | None = None) -> None:
    bag = _session(session)
    bag.pop(CONTEXT_KEY, None)


def context_banner_text(ctx: dict[str, Any] | None) -> str | None:
    if not ctx:
        return None
    price = float(ctx.get("my_price_psf") or 0)
    verdict = ctx.get("verdict") or "—"
    project = ctx.get("project") or "—"
    age = format_relative_age(ctx.get("updated_at"))
    return f"Continuing Hub decision: {project} @ ₹{price:,.0f}/sqft · {verdict} · {age}"


def format_relative_age(
    iso: str | None,
    *,
    now: datetime | None = None,
) -> str:
    """Human freshness for open decision — Bloomberg-style honesty."""
    if not iso:
        return "No open decision yet"
    try:
        raw = str(iso).strip()
        if raw.endswith("Z"):
            raw = raw[:-1] + "+00:00"
        then = datetime.fromisoformat(raw)
        if then.tzinfo is None:
            then = then.replace(tzinfo=timezone.utc)
        current = now or datetime.now(timezone.utc)
        if current.tzinfo is None:
            current = current.replace(tzinfo=timezone.utc)
        seconds = max(0, int((current - then.astimezone(timezone.utc)).total_seconds()))
    except (TypeError, ValueError):
        return "No open decision yet"
    if seconds < 45:
        return "Updated just now"
    if seconds < 3600:
        mins = max(1, seconds // 60)
        return f"Updated {mins}m ago"
    if seconds < 86400:
        hours = max(1, seconds // 3600)
        return f"Updated {hours}h ago"
    days = max(1, seconds // 86400)
    return f"Updated {days}d ago"


def context_signature(ctx: dict[str, Any] | None) -> str:
    if not ctx:
        return ""
    return (
        f"{ctx.get('project')}|{float(ctx.get('my_price_psf') or 0):.0f}|"
        f"{ctx.get('verdict')}|{ctx.get('threat_score')}"
    )


def safe_toast(message: str, *, icon: str = "✅") -> None:
    try:
        import streamlit as st

        st.toast(message, icon=icon)
    except Exception:
        pass


def _session(session: dict[str, Any] | None) -> dict[str, Any]:
    if session is not None:
        return session
    import streamlit as st

    return st.session_state  # type: ignore[return-value]
