"""
Executive Decision Sheet — CEO 10-second understanding on every module.

Composes existing tokens + KPI patterns. Does not duplicate scoring engines.
"""
from __future__ import annotations

import html

import streamlit as st

from components.kpi_cards import render_kpi_cards
from models.decision import DecisionBrief, JourneyStep


_RISK_COLOR = {
    "LOW": "#3dd68c",
    "MEDIUM": "#f0b429",
    "HIGH": "#ff8c42",
    "CRITICAL": "#ff4b4b",
}


def render_executive_sheet(brief: DecisionBrief, *, key: str = "eds") -> None:
    """Mount at top of a workspace after login / hero."""
    color = _RISK_COLOR.get(brief.risk_level, "#f0b429")
    score_html = (
        f'<span class="iq-eds-score">{int(brief.risk_score)}</span>'
        if brief.risk_score is not None
        else ""
    )
    insights = "".join(f"<li>{html.escape(x)}</li>" for x in brief.key_insights[:6])
    drivers = "".join(f"<li>{html.escape(x)}</li>" for x in brief.drivers[:5])
    honesty = "".join(f"<li>{html.escape(x)}</li>" for x in brief.honesty_notes[:3])

    fin = ""
    if brief.financial_impact_cr is not None:
        fin = (
            f'<div class="iq-eds-fin"><span>{html.escape(brief.financial_impact_label or "Impact")}</span>'
            f"<strong>{brief.financial_impact_cr:,.1f}</strong></div>"
        )

    st.html(
        f"""
        <div class="iq-eds" role="region" aria-label="Executive decision sheet">
          <div class="iq-eds-top">
            <div>
              <div class="iq-eds-kicker">Executive Decision Sheet · {html.escape(brief.module)}</div>
              <h2 class="iq-eds-summary">{html.escape(brief.executive_summary)}</h2>
            </div>
            <div class="iq-eds-risk" style="border-color:{color};">
              <div class="iq-eds-risk-label">Risk</div>
              <div class="iq-eds-risk-val" style="color:{color};">{html.escape(brief.risk_level)}{score_html}</div>
            </div>
          </div>
          <div class="iq-eds-grid">
            <div class="iq-eds-panel">
              <h4>Key insights</h4>
              <ul>{insights or "<li>No insights loaded</li>"}</ul>
            </div>
            <div class="iq-eds-panel">
              <h4>Business impact</h4>
              <p>{html.escape(brief.business_impact or "—")}</p>
              {fin}
            </div>
            <div class="iq-eds-panel iq-eds-ai">
              <h4>AI recommendation</h4>
              <p>{html.escape(brief.ai_recommendation or "—")}</p>
              <div class="iq-eds-conf">{html.escape(brief.confidence or "")}</div>
            </div>
          </div>
          {f'<div class="iq-eds-panel"><h4>Key drivers</h4><ul>{drivers}</ul></div>' if drivers else ""}
          {f'<div class="iq-eds-honesty"><ul>{honesty}</ul></div>' if honesty else ""}
        </div>
        """
    )

    if brief.suggested_actions:
        render_kpi_cards(
            [
                {
                    "label": f"Action {i}",
                    "value": a[:80] + ("…" if len(a) > 80 else ""),
                    "format": "str",
                }
                for i, a in enumerate(brief.suggested_actions[:3], 1)
            ]
        )
        with st.expander("All suggested actions", expanded=False):
            for i, a in enumerate(brief.suggested_actions, 1):
                st.markdown(f"**{i}.** {a}")

    _render_next_cta(brief.next_step, key=key)


def _render_next_cta(step: JourneyStep | None, *, key: str) -> None:
    if not step:
        st.caption("Journey complete — export the board pack from Reports.")
        return
    st.html(
        f'<div class="iq-eds-next">'
        f'<div class="iq-eds-next-label">Guided next step</div>'
        f"<strong>{html.escape(step.label)}</strong>"
        f'<span>{html.escape(step.reason)}</span></div>'
    )
    if st.button(
        f"Continue → {step.label}",
        type="primary",
        width="stretch",
        key=f"{key}_next_{step.path}",
    ):
        st.session_state["dss_nav_label"] = step.label
        st.session_state["dss_nav_label_committed"] = step.label
        st.session_state["dss_nav_target"] = step.path
        st.session_state["dss_module_nav"] = step.label
        st.switch_page(step.path)
