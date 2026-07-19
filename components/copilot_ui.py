"""Launch Decision Co-pilot UI — one real-world decision surface."""
from __future__ import annotations

import html

import streamlit as st

from services.launch_copilot_service import LaunchVerdict


def threat_gauge(score: int, verdict: str, color: str) -> None:
    """Animated SVG gauge — race HUD speedometer language."""
    angle = -90 + (score / 100) * 180
    st.html(
        f"""
        <div class="copilot-gauge-wrap">
          <svg viewBox="0 0 240 140" class="copilot-gauge" role="img" aria-label="Launch threat score {score}">
            <defs>
              <linearGradient id="gArc" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stop-color="#3dff9a"/>
                <stop offset="55%" stop-color="#ffc048"/>
                <stop offset="100%" stop-color="#ff3b4a"/>
              </linearGradient>
              <filter id="gGlow" x="-20%" y="-20%" width="140%" height="140%">
                <feGaussianBlur stdDeviation="2.5" result="b"/>
                <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
              </filter>
            </defs>
            <path d="M20 120 A100 100 0 0 1 220 120" fill="none" stroke="#1a2433" stroke-width="18" stroke-linecap="round"/>
            <path d="M20 120 A100 100 0 0 1 220 120" fill="none" stroke="url(#gArc)" stroke-width="18"
                  stroke-linecap="round" opacity="0.95" filter="url(#gGlow)"/>
            <g transform="rotate({angle:.1f} 120 120)">
              <line x1="120" y1="120" x2="120" y2="38" stroke="#ffc048" stroke-width="4" stroke-linecap="round"/>
              <circle cx="120" cy="120" r="9" fill="{html.escape(color)}" stroke="#fff" stroke-width="1.5"/>
            </g>
            <text x="120" y="98" text-anchor="middle" fill="#fff" font-size="30" font-weight="800" font-family="Exo 2,sans-serif">{score}</text>
            <text x="120" y="116" text-anchor="middle" fill="{html.escape(color)}" font-size="13" font-weight="800" letter-spacing="1.5" font-family="Exo 2,sans-serif">{html.escape(verdict)}</text>
          </svg>
          <div class="copilot-gauge-caption">THREAT TACHO · 0 CLEAR → 100 ABORT</div>
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
