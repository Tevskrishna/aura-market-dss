"""
Today's Executive Brief — Hub-only briefing card.
Uses existing LaunchVerdict fields. No new scoring.
"""
from __future__ import annotations

import html

import streamlit as st

from services.decision_context import format_relative_age
from services.launch_copilot_service import LaunchVerdict


def render_executive_brief(v: LaunchVerdict, *, updated_at: str | None = None) -> None:
    """
    Calm morning brief for CEOs.
    Simulated directional twin figures remain labelled via existing honesty banners elsewhere.
    """
    age = format_relative_age(updated_at)
    risk = html.escape(str(v.threat_score))
    conf = "Model · competition seed + twin + margin (see honesty banner)"
    next_step = "Continue → Market Intelligence to validate demand evidence."
    if (v.verdict or "").upper() == "NO-GO":
        next_step = "Continue → Competition & Scenario Engine before any brochure spend."
    elif (v.verdict or "").upper() == "HOLD":
        next_step = "Continue → Decision Explanation after Market & Competition evidence."

    risks = html.escape(
        f"Threat {v.threat_score}/100 · nearest rival {v.rival_name} @ ₹{v.rival_price_psf:,.0f}/sqft · "
        f"UC pressure {v.uc_pressure_units:,} units"
    )
    opportunity = html.escape(
        f"Recoverable ≈ ₹{v.recovery_cr} Cr with intervene vs blind-spot ≈ ₹{v.blind_spot_loss_cr} Cr"
    )
    action = html.escape((v.actions[0] if v.actions else "Review suggested actions below.")[:140])

    st.html(
        f"""
        <section class="iq-exec-brief" aria-label="Today's Executive Brief">
          <div class="iq-exec-brief-kicker">Today's Executive Brief · {html.escape(age)}</div>
          <div class="iq-exec-brief-grid">
            <div class="iq-exec-brief-cell">
              <span>Project</span>
              <strong>{html.escape(v.project)}</strong>
            </div>
            <div class="iq-exec-brief-cell">
              <span>Current decision</span>
              <strong class="iq-exec-brief-verdict" style="color:{html.escape(v.verdict_color)}">{html.escape(v.verdict)}</strong>
            </div>
            <div class="iq-exec-brief-cell">
              <span>Confidence</span>
              <strong>{html.escape(conf)}</strong>
            </div>
            <div class="iq-exec-brief-cell">
              <span>Risk score</span>
              <strong>{risk} / 100</strong>
            </div>
            <div class="iq-exec-brief-cell iq-exec-brief-wide">
              <span>Key risks</span>
              <strong>{risks}</strong>
            </div>
            <div class="iq-exec-brief-cell iq-exec-brief-wide">
              <span>Business opportunity</span>
              <strong>{opportunity}</strong>
            </div>
            <div class="iq-exec-brief-cell iq-exec-brief-wide">
              <span>Recommended next step</span>
              <strong>{html.escape(next_step)}</strong>
            </div>
            <div class="iq-exec-brief-cell">
              <span>Top action</span>
              <strong>{action}</strong>
            </div>
            <div class="iq-exec-brief-cell">
              <span>Est. review time</span>
              <strong>~10 min full journey · ~30s for this brief</strong>
            </div>
          </div>
        </section>
        """
    )
