"""
Executive Decision Sheet — CEO understanding + guided journey chrome.

Modes (product rule — one final recommendation only on Hub):
  final    — Executive Hub GO/HOLD/NO-GO
  evidence — supporting modules (market, competition, …)
  why      — AI Recommendations explains Hub decision (no second verdict)
  board    — Reports close / board pack (locked Hub call reference)
"""
from __future__ import annotations

import html
from typing import Literal

import streamlit as st

from components.kpi_cards import render_kpi_cards
from models.decision import DecisionBrief, JourneyStep
from services.decision_brief_service import DECISION_JOURNEY, journey_index, prev_before
from services.decision_context import format_relative_age, get_decision_context

SheetMode = Literal["final", "evidence", "why", "board"]

_RISK_COLOR = {
    "LOW": "#3dd68c",
    "MEDIUM": "#f0b429",
    "HIGH": "#ff8c42",
    "CRITICAL": "#ff4b4b",
}

_MODE_KICKER = {
    "final": "Final launch recommendation · Hub only",
    "evidence": "Evidence · supports the Hub call",
    "why": "Decision explanation · not a second GO/HOLD",
    "board": "Board pack · locked Hub decision",
}

_AI_TITLE = {
    "final": "Final AI recommendation",
    "evidence": "Evidence insight",
    "why": "How evidence supports the Hub",
    "board": "Locked Hub call",
}


def render_open_project_chip() -> None:
    """Global project selected on Hub — shown on every guided step."""
    ctx = get_decision_context()
    if not ctx:
        st.caption("Select project + ₹/sqft once on **Executive Hub** — it carries through this journey.")
        return
    price = float(ctx.get("my_price_psf") or 0)
    verdict = html.escape(str(ctx.get("verdict") or "—"))
    project = html.escape(str(ctx.get("project") or "—"))
    age = html.escape(format_relative_age(ctx.get("updated_at")))
    st.html(
        f'<div class="iq-open-project" role="status">'
        f'<span class="iq-open-project-kicker">Open project</span>'
        f"<strong>{project}</strong>"
        f'<span>₹{price:,.0f}/sqft · Hub {verdict} · {age}</span>'
        f"</div>"
    )


def render_journey_progress(module_label: str) -> None:
    """Step X of N — current / done / remaining + ETA + purpose strip."""
    from components.journey_meta import JOURNEY_ETA_MIN, PAGE_PURPOSE

    idx = journey_index(module_label)
    total = len(DECISION_JOURNEY)
    if idx < 0:
        st.caption("Evidence workspace · return to the guided journey via Continue on Hub.")
        return

    step = idx + 1
    pct = int(100 * step / total)
    eta = JOURNEY_ETA_MIN.get(module_label, max(1, total - idx))
    purpose = PAGE_PURPOSE.get(module_label, {})
    question = purpose.get("question") or DECISION_JOURNEY[idx].reason
    why = purpose.get("why", "")
    outcome = purpose.get("outcome", "")
    supports = purpose.get("supports", "")
    nxt = DECISION_JOURNEY[idx + 1] if idx + 1 < total else None
    next_hint = (
        f"Next: Continue → {nxt.label}"
        if nxt
        else "Next: download the board pack"
    )

    # Pipeline dots: done / current / remaining
    dots = []
    for i, s in enumerate(DECISION_JOURNEY):
        short = html.escape(s.label.split()[0])
        if i < idx:
            cls = "iq-pipe-done"
            mark = "✓"
        elif i == idx:
            cls = "iq-pipe-now"
            mark = str(i + 1)
        else:
            cls = "iq-pipe-todo"
            mark = str(i + 1)
        dots.append(
            f'<div class="iq-pipe-step {cls}" title="{html.escape(s.label)}">'
            f'<span class="iq-pipe-dot">{mark}</span>'
            f'<span class="iq-pipe-lab">{short}</span></div>'
        )

    st.html(
        f'<div class="iq-purpose" role="note" aria-label="Page purpose">'
        f'<div class="iq-purpose-row"><span class="iq-purpose-label">Why here</span>'
        f'<span>{html.escape(why)}</span></div>'
        f'<div class="iq-purpose-row iq-purpose-q"><span class="iq-purpose-label">Question</span>'
        f'<strong>{html.escape(question)}</strong></div>'
        f'<div class="iq-purpose-row"><span class="iq-purpose-label">Outcome</span>'
        f'<span>{html.escape(outcome)}</span></div>'
        f'<div class="iq-purpose-row"><span class="iq-purpose-label">Supports Hub</span>'
        f'<span>{html.escape(supports)}</span></div>'
        f'<div class="iq-purpose-row iq-purpose-next"><span class="iq-purpose-label">Do next</span>'
        f'<span>{html.escape(next_hint)}</span></div>'
        f"</div>"
        f'<div class="iq-journey-progress" role="navigation" aria-label="Decision journey">'
        f'<div class="iq-journey-progress-top">'
        f"<strong>Step {step} of {total}</strong>"
        f'<span>~{eta} min remaining · {html.escape(module_label)}</span></div>'
        f'<div class="iq-journey-track"><div class="iq-journey-fill" style="width:{pct}%"></div></div>'
        f'<div class="iq-pipe" aria-hidden="true">{"".join(dots)}</div>'
        f"</div>"
    )


def render_executive_sheet(
    brief: DecisionBrief,
    *,
    key: str = "eds",
    mode: SheetMode = "evidence",
    show_actions: bool | None = None,
) -> None:
    """
    Mount decision / evidence sheet.
    Hub uses mode='final'. Recs uses mode='why'. Reports uses mode='board'.
    """
    if show_actions is None:
        show_actions = mode == "final"

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

    ctx = get_decision_context()
    freshness = format_relative_age(ctx.get("updated_at") if ctx else None)
    kicker = _MODE_KICKER.get(mode, _MODE_KICKER["evidence"])
    ai_title = _AI_TITLE.get(mode, _AI_TITLE["evidence"])
    risk_label = {
        "final": "Hub risk",
        "why": "Evidence weight",
        "board": "Locked Hub risk",
        "evidence": "Module signal",
    }.get(mode, "Module signal")

    st.html(
        f"""
        <div class="iq-eds iq-eds-{html.escape(mode)}" role="region" aria-label="{html.escape(kicker)}">
          <div class="iq-live-strip" style="margin:0 0 0.75rem;padding:0.35rem 0.55rem;">
            <span class="iq-live-dot" aria-hidden="true"></span>
            <span class="iq-live-label">{html.escape(kicker)}</span>
            <span class="iq-live-meta">{html.escape(brief.module)} · {html.escape(freshness)}</span>
          </div>
          <div class="iq-eds-top">
            <div>
              <div class="iq-eds-kicker">{html.escape(brief.module)}</div>
              <h2 class="iq-eds-summary">{html.escape(brief.executive_summary)}</h2>
            </div>
            <div class="iq-eds-risk" style="border-color:{color};">
              <div class="iq-eds-risk-label">{html.escape(risk_label)}</div>
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
              <h4>{html.escape(ai_title)}</h4>
              <p>{html.escape(brief.ai_recommendation or "—")}</p>
              <div class="iq-eds-conf">{html.escape(brief.confidence or "")}</div>
            </div>
          </div>
          {f'<div class="iq-eds-panel"><h4>Key drivers</h4><ul>{drivers}</ul></div>' if drivers else ""}
          {f'<div class="iq-eds-honesty"><ul>{honesty}</ul></div>' if honesty else ""}
        </div>
        """
    )

    if show_actions and brief.suggested_actions:
        st.caption("Suggested actions for the **Hub** final call (only shown here on Executive Hub).")
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

    _render_journey_nav(brief, key=key)


def _render_journey_nav(brief: DecisionBrief, *, key: str) -> None:
    prev = prev_before(brief.module)
    nxt = brief.next_step
    c1, c2 = st.columns(2)
    with c1:
        if prev:
            if st.button(
                f"← Previous · {prev.label}",
                width="stretch",
                key=f"{key}_prev_{prev.path}",
            ):
                from components.touch_nav import navigate_to

                navigate_to(prev.label, prev.path)
        else:
            st.caption("Journey start · Executive Hub")
    with c2:
        if nxt:
            st.html(
                f'<div class="iq-eds-next" style="margin:0 0 0.5rem;">'
                f'<div class="iq-eds-next-label">Continue</div>'
                f"<strong>{html.escape(nxt.label)}</strong>"
                f'<span>{html.escape(nxt.reason)}</span></div>'
            )
            if st.button(
                f"Continue → {nxt.label}",
                type="primary",
                width="stretch",
                key=f"{key}_next_{nxt.path}",
            ):
                from components.touch_nav import navigate_to

                navigate_to(nxt.label, nxt.path)
        else:
            st.success("Journey complete — download the board pack below.")
