"""Launch Decision Co-pilot UI — one real-world decision surface."""
from __future__ import annotations

import html

import streamlit as st

from services.launch_copilot_service import LaunchVerdict


def threat_gauge(score: int, verdict: str, color: str) -> None:
    """Animated SVG gauge — feels like a product, not a metric card."""
    # Needle angle: 0 score = -90deg (left), 100 = +90deg (right)
    angle = -90 + (score / 100) * 180
    st.html(
        f"""
        <div class="copilot-gauge-wrap">
          <svg viewBox="0 0 240 140" class="copilot-gauge" role="img" aria-label="Launch threat score {score}">
            <defs>
              <linearGradient id="gArc" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stop-color="#3dd68c"/>
                <stop offset="55%" stop-color="#f0b429"/>
                <stop offset="100%" stop-color="#ff4b4b"/>
              </linearGradient>
            </defs>
            <path d="M20 120 A100 100 0 0 1 220 120" fill="none" stroke="#30363d" stroke-width="18" stroke-linecap="round"/>
            <path d="M20 120 A100 100 0 0 1 220 120" fill="none" stroke="url(#gArc)" stroke-width="18"
                  stroke-linecap="round" stroke-dasharray="314" stroke-dashoffset="0" opacity="0.95"/>
            <g transform="rotate({angle:.1f} 120 120)">
              <line x1="120" y1="120" x2="120" y2="38" stroke="#e6edf3" stroke-width="4" stroke-linecap="round"/>
              <circle cx="120" cy="120" r="8" fill="{html.escape(color)}"/>
            </g>
            <text x="120" y="100" text-anchor="middle" fill="#fff" font-size="28" font-weight="800" font-family="Inter,sans-serif">{score}</text>
            <text x="120" y="118" text-anchor="middle" fill="{html.escape(color)}" font-size="14" font-weight="800" font-family="Inter,sans-serif">{html.escape(verdict)}</text>
          </svg>
          <div class="copilot-gauge-caption">LAUNCH THREAT SCORE · 0 safe → 100 abort</div>
        </div>
        """
    )


def verdict_banner(v: LaunchVerdict) -> None:
    st.html(
        f"""
        <div class="copilot-banner" style="border-color:{html.escape(v.verdict_color)};">
          <div class="copilot-banner-kicker">REAL-WORLD DECISION</div>
          <h2 style="color:{html.escape(v.verdict_color)};margin:0.2rem 0 0.4rem;">{html.escape(v.verdict)} · {html.escape(v.project)}</h2>
          <p>{html.escape(v.headline)}</p>
        </div>
        """
    )


def factor_bars(v: LaunchVerdict) -> None:
    rows = []
    for label, pts, note in v.factors:
        width = max(min(pts, 40), 2) * 2.2
        rows.append(
            f'<div class="copilot-factor">'
            f'<div class="copilot-factor-top"><span>{html.escape(label)}</span><strong>+{pts}</strong></div>'
            f'<div class="copilot-factor-track"><div class="copilot-factor-fill" style="width:{width}%"></div></div>'
            f'<div class="copilot-factor-note">{html.escape(note)}</div></div>'
        )
    st.html(f'<div class="copilot-factors">{"".join(rows)}</div>')


def action_cards(actions: list[str]) -> None:
    cards = []
    for i, a in enumerate(actions, 1):
        cards.append(
            f'<div class="copilot-action"><div class="copilot-action-num">{i:02d}</div>'
            f'<div>{html.escape(a)}</div></div>'
        )
    st.html(f'<div class="copilot-actions">{"".join(cards)}</div>')
