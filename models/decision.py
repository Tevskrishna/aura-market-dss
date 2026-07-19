"""Shared executive decision brief — one model for Hub → modules → board pack."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class JourneyStep:
    label: str
    path: str
    reason: str = ""


@dataclass(frozen=True)
class DecisionBrief:
    """
    CEO 10-second sheet. Services fill this; UI only renders.
    Never invent a second scoring engine — adapters map existing verdicts.
    """

    module: str
    executive_summary: str
    key_insights: list[str] = field(default_factory=list)
    business_impact: str = ""
    ai_recommendation: str = ""
    risk_level: str = "MEDIUM"  # LOW | MEDIUM | HIGH | CRITICAL
    risk_score: int | None = None  # 0–100 when available
    suggested_actions: list[str] = field(default_factory=list)
    financial_impact_label: str = ""
    financial_impact_cr: float | None = None
    confidence: str = ""  # e.g. "High · seed-backed"
    drivers: list[str] = field(default_factory=list)
    next_step: JourneyStep | None = None
    honesty_notes: list[str] = field(default_factory=list)
