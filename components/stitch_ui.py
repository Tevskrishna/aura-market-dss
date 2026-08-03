"""
Stitch institutional UI primitives — Hub hero, Market snapshot, Evidence Vault.
Maps Google Stitch HTML into Streamlit-safe HTML fragments.
"""
from __future__ import annotations

import base64
import html
from pathlib import Path

import streamlit as st

from config import settings

_HERO_CACHE: str | None = None

VERDICT_CLASS = {
    "GO": "go",
    "HOLD": "hold",
    "NO-GO": "nogo",
    "NOGO": "nogo",
}

LIFECYCLE = [
    "Executive Hub",
    "Market Intelligence",
    "Competition & Land",
    "Scenario Engine",
    "Decision Explanation",
    "Reports",
]


def hero_bg_data_uri() -> str:
    global _HERO_CACHE
    if _HERO_CACHE:
        return _HERO_CACHE
    path = settings.ASSETS_DIR / "graphics" / "hero-bengaluru-night.jpg"
    if not path.exists():
        path = settings.ASSETS_DIR / "graphics" / "hero-bagaluru-day.jpg"
    raw = path.read_bytes() if path.exists() else b""
    if raw:
        _HERO_CACHE = "data:image/jpeg;base64," + base64.b64encode(raw).decode("ascii")
    else:
        _HERO_CACHE = ""
    return _HERO_CACHE


def render_impl_map_tabs() -> None:
    """Show what Stitch screens are being mapped into the live app."""
    t1, t2, t3 = st.tabs(["Hub (Stitch)", "Market (Stitch)", "App-wide shell"])
    with t1:
        st.html(
            """
            <div class="st-impl-map">
              <h4>Implementing now — Executive Hub</h4>
              <ul>
                <li>Full-bleed Bagaluru hero + Playfair headline</li>
                <li>Project + ₹/sqft controls → live GO / HOLD / NO-GO engine</li>
                <li>Forest / amber / burgundy verdict panel (Risk + Exposure)</li>
                <li>Do this week · Risk Detail · Evidence Vault · 6-step lifecycle</li>
              </ul>
            </div>
            """
        )
    with t2:
        st.html(
            """
            <div class="st-impl-map">
              <h4>Implementing now — Market Intelligence</h4>
              <ul>
                <li>Bagaluru Snapshot strip: 83% · 12 · 10,283 · 1,741</li>
                <li>Weighted price trend (Plotly, terracotta)</li>
                <li>PropStack project table with absorption bars</li>
              </ul>
            </div>
            """
        )
    with t3:
        st.html(
            """
            <div class="st-impl-map">
              <h4>Shell across stakeholder path</h4>
              <ul>
                <li>Warm stone #fbf9f8 canvas · Playfair + Geist</li>
                <li>Terracotta #B97343 accent · 6-step IC nav</li>
                <li>Competition · Scenario · Explanation · Reports inherit shell</li>
              </ul>
            </div>
            """
        )


def render_topbar() -> None:
    """Institutional actions strip — matches Stitch Hub / Market HTML."""
    st.html(
        """
        <div class="st-topbar">
          <span class="st-btn-ghost">Export report</span>
          <span class="st-btn-solid">Board review</span>
        </div>
        """
    )


def begin_stitch_page() -> None:
    """Shared page chrome start — call once near the top of every authenticated view."""
    render_topbar()


def end_stitch_page(active_label: str) -> None:
    """Shared page chrome end — IC lifecycle + institutional footer."""
    render_lifecycle(active_label)
    st.html(
        '<p class="st-footer">RealEstateIQ Institutional · Puravankara · Bagaluru micro-market</p>'
    )


def render_hub_hero(
    *,
    project: str,
    price_psf: float,
    verdict: str,
    threat_score: int,
    exposure_cr: float,
    headline: str,
) -> None:
    v = (verdict or "HOLD").upper().replace(" ", "-")
    klass = VERDICT_CLASS.get(v, VERDICT_CLASS.get(v.replace("-", ""), "hold"))
    risk_label = "Low" if threat_score < 35 else ("Medium" if threat_score < 65 else "High")
    bg = hero_bg_data_uri()
    bg_css = f"background-image:url('{bg}');" if bg else "background:#1c1b1b;"
    st.html(
        f"""
        <section class="st-hero" aria-label="Executive launch decision">
          <div class="st-hero-media" style="{bg_css}"></div>
          <div class="st-hero-scrim"></div>
          <div class="st-hero-copy">
            <div class="st-hero-kicker">RealEstateIQ | Puravankara · Bagaluru</div>
            <h1 class="st-hero-title">Should we launch at this price?</h1>
            <p class="st-hero-sub">{html.escape(headline or "PropStack Bagaluru absorption supports a priced launch call — set ₹/sqft and read the model verdict.")}</p>
            <p style="margin:0;font-size:0.85rem;opacity:0.8;letter-spacing:0.06em;text-transform:uppercase;">
              Open project · {html.escape(project)} · ₹{price_psf:,.0f}/sqft
            </p>
          </div>
          <div class="st-hero-panel {klass}">
            <div class="st-hero-panel-kicker">Model verdict</div>
            <div class="st-hero-verdict">{html.escape(v)}</div>
            <div class="st-hero-meta">
              <div><span>Risk index</span><strong>{html.escape(risk_label)} · {int(threat_score)}</strong></div>
              <div><span>Exposure</span><strong>₹ {exposure_cr:,.0f} Cr</strong></div>
            </div>
            <p class="st-hero-note">Directional twin + PropStack competition set — see data contract.</p>
          </div>
        </section>
        """
    )


def render_do_this_week(actions: list[str]) -> None:
    items = actions[:3] if actions else [
        "Review Market Intelligence absorption evidence",
        "Pressure-test rival month in Scenario Engine",
        "Lock board pack from Reports before IC",
    ]
    dues = ["Priority", "This week", "Before IC"]
    rows = []
    for i, a in enumerate(items):
        rows.append(
            f'<div class="st-week-item"><p>{html.escape(a[:120])}</p>'
            f'<span>{dues[i] if i < len(dues) else "Next"}</span></div>'
        )
    st.html(
        f'<h3 class="st-section-title">Do this week</h3><div>{"".join(rows)}</div>'
    )


def render_evidence_vault() -> None:
    st.html(
        """
        <h3 class="st-section-title">Evidence Vault</h3>
        <div class="st-vault">
          <div class="st-vault-card"><div class="mark">◆</div><strong>Market</strong><span>Bagaluru absorption &amp; price</span></div>
          <div class="st-vault-card"><div class="mark">◆</div><strong>Competition</strong><span>RERA · UC · land</span></div>
          <div class="st-vault-card"><div class="mark">◆</div><strong>Scenario</strong><span>Rival &amp; intervene paths</span></div>
          <div class="st-vault-card"><div class="mark">◆</div><strong>Reports</strong><span>Board decision pack</span></div>
        </div>
        """
    )


def render_lifecycle(active_label: str = "Executive Hub") -> None:
    # Analyst labs (Buyer, DMAIC, …) sit beside the IC spine — do not fake progress.
    prior = LIFECYCLE.index(active_label) if active_label in LIFECYCLE else -1
    steps = []
    for i, label in enumerate(LIFECYCLE):
        on = prior >= 0 and i <= prior
        current = prior >= 0 and i == prior
        short = label.replace("Intelligence", "Intel").replace("Explanation", "Explain")
        steps.append(
            f'<div class="st-lifecycle-step{" current" if current else ""}">'
            f'<div class="st-lifecycle-dot {"on" if on else ""}">{i + 1}</div>'
            f'<p>{html.escape(short)}</p></div>'
        )
    st.html(
        '<p class="st-nav-caption" style="text-align:center;margin-top:1.5rem;">Approval lifecycle</p>'
        f'<div class="st-lifecycle">{"".join(steps)}</div>'
    )


def render_bagaluru_snapshot(summary: dict | None) -> None:
    """Dark institutional strip — counters run when scrolled into view."""
    from components.scroll_motion import inject_scroll_motion

    if not summary:
        st.html(
            """
            <section class="st-snap st-count-root" aria-label="Bagaluru snapshot">
              <div class="st-snap-accent"></div>
              <div class="st-snap-head">
                <p class="st-snap-title">Bagaluru Snapshot</p>
                <p class="st-snap-velocity"><span>Market velocity</span><strong>—</strong></p>
              </div>
              <div class="st-snap-grid">
                <div class="st-snap-cell"><span>Market absorption</span><strong>—</strong></div>
                <div class="st-snap-cell"><span>Active assets</span><strong>—</strong></div>
                <div class="st-snap-cell"><span>Total inventory</span><strong>—</strong></div>
                <div class="st-snap-cell"><span>Available units</span><strong>—</strong></div>
              </div>
              <div class="st-snap-foot">PropStack summary not loaded</div>
            </section>
            """
        )
        inject_scroll_motion()
        return

    abs_n = float(summary.get("absorption_pct", 0))
    projects_n = int(summary.get("projects", 0))
    total_n = int(summary.get("total_units", 0))
    avail_n = int(summary.get("units_unsold", 0))
    period = html.escape(str(summary.get("period_label", "Dec 2022 - Nov 2025")))
    foot = (
        f"{abs_n:.0f}% Absorbed · {projects_n} projects · {total_n:,} units · "
        f"{avail_n:,} available · {period}"
    )
    st.html(
        f"""
        <section class="st-snap st-count-root" aria-label="Bagaluru snapshot">
          <div class="st-snap-accent"></div>
          <div class="st-snap-head">
            <p class="st-snap-title">Bagaluru Snapshot</p>
            <p class="st-snap-velocity">
              <span>Market velocity</span>
              <strong class="st-count" data-target="{abs_n}" data-suffix="% Absorbed" data-decimals="0" data-duration="1600">0% Absorbed</strong>
            </p>
          </div>
          <div class="st-snap-grid">
            <div class="st-snap-cell">
              <span>Market absorption</span>
              <strong class="st-count" data-target="{abs_n}" data-suffix="%" data-decimals="0" data-duration="1500">0%</strong>
            </div>
            <div class="st-snap-cell">
              <span>Active assets</span>
              <strong class="st-count" data-target="{projects_n}" data-decimals="0" data-duration="1200">0</strong>
            </div>
            <div class="st-snap-cell">
              <span>Total inventory</span>
              <strong class="st-count" data-target="{total_n}" data-decimals="0" data-duration="1700">0</strong>
            </div>
            <div class="st-snap-cell">
              <span>Available units</span>
              <strong class="st-count" data-target="{avail_n}" data-decimals="0" data-duration="1600">0</strong>
            </div>
          </div>
          <div class="st-snap-foot">{html.escape(foot)}</div>
        </section>
        """
    )
    inject_scroll_motion()


def _status_badge(status: str, absorption: float) -> tuple[str, str]:
    s = (status or "").strip().lower()
    if absorption >= 95 or "sold" in s:
        return "sold", "Sold out"
    if absorption >= 75:
        return "stable", "Stable"
    if absorption >= 55:
        return "boom", "Booming"
    if "ready" in s:
        return "ready", "Ready"
    return "uc", "Under construction"


def _risk_score(absorption: float) -> tuple[str, str]:
    # Lower score = healthier inventory (Stitch editorial scale)
    if absorption >= 90:
        return f"{max(1.2, 10 - absorption / 12):.1f}", "Optimal"
    if absorption >= 70:
        return f"{max(2.0, 9 - absorption / 15):.1f}", "Stable"
    if absorption >= 50:
        return f"{min(4.5, 8 - absorption / 20):.1f}", "Monitoring"
    return f"{min(7.5, 9 - absorption / 25):.1f}", "Elevated"


def render_portfolio_table(df) -> None:
    """Micro-market portfolio — HTML table with absorption bars (Stitch)."""
    if df is None or getattr(df, "empty", True):
        st.info("No projects in this view.")
        return
    rows = []
    for _, r in df.iterrows():
        name = html.escape(str(r.get("project", "—")))
        dev = html.escape(str(r.get("developer", "")))
        price = float(r.get("price_psf", 0) or 0)
        abs_pct = float(r.get("absorption_pct", 0) or 0)
        status_raw = str(r.get("status", ""))
        badge_cls, badge_lbl = _status_badge(status_raw, abs_pct)
        risk_n, risk_lbl = _risk_score(abs_pct)
        inv = int(r.get("units_unsold", 0) or 0)
        rows.append(
            f"""
            <tr>
              <td>
                <strong class="st-pt-name">{name}</strong>
                <span class="st-pt-sub">{dev}</span>
              </td>
              <td class="st-pt-mono">₹{price:,.0f}</td>
              <td>
                <div class="st-pt-abs">
                  <div class="st-pt-bar"><i style="--bar-w:{max(0, min(100, abs_pct)):.0f}%"></i></div>
                  <span>{abs_pct:.0f}%</span>
                </div>
              </td>
              <td class="st-pt-mono">{inv:,}</td>
              <td><span class="st-pt-badge {badge_cls}">{html.escape(badge_lbl)}</span></td>
              <td class="st-pt-risk">
                <strong>{risk_n}</strong>
                <span>{html.escape(risk_lbl)}</span>
              </td>
            </tr>
            """
        )
    st.html(
        f"""
        <div class="st-pt-wrap">
          <table class="st-pt">
            <thead>
              <tr>
                <th>Project name</th>
                <th>Pricing (avg.)</th>
                <th>Absorption</th>
                <th>Inventory</th>
                <th>Status</th>
                <th>Risk score</th>
              </tr>
            </thead>
            <tbody>{"".join(rows)}</tbody>
          </table>
        </div>
        """
    )
    from components.scroll_motion import inject_scroll_motion

    inject_scroll_motion()


def stitch_brand_sidebar_html(project: str | None = None) -> str:
    proj = html.escape(project or "Bagaluru launch")
    return (
        '<div class="st-brand">'
        '<p class="st-brand-name">RealEstateIQ</p>'
        '<div class="st-brand-chip">'
        '<div class="st-brand-chip-mark">▣</div>'
        f"<div><strong>{proj}</strong><span>Bagaluru development</span></div>"
        "</div></div>"
    )
