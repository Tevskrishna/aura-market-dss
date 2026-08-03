"""Always-visible measured / seed / simulated data contract — Hub trust strip."""
from __future__ import annotations

import streamlit as st


def render_data_contract(*, compact: bool = False) -> None:
    """Enterprise honesty — first thing a CTO/CEO should see."""
    if compact:
        st.caption(
            "**Data contract:** PropStack Bagaluru projects/market series · Measured bookings/SMC · "
            "Simulated scenario ₹ Cr · Illustrative map (if opened). Not live KRERA unless configured."
        )
        return
    st.html(
        """
        <div class="iq-data-contract" role="note" aria-label="Data contract">
          <div class="iq-data-contract-kicker">Data contract · Bagaluru Aerospace Highway pilot</div>
          <div class="iq-data-contract-grid">
            <div><span>PropStack</span><strong>Projects · inventory · price trends</strong></div>
            <div><span>Measured</span><strong>Bookings · SMC spend</strong></div>
            <div><span>Simulated</span><strong>Scenario engine ₹ Cr (directional)</strong></div>
            <div><span>Curated / illustrative</span><strong>Land · upcoming · map (Quality Lab)</strong></div>
          </div>
          <p>Market numbers from Bagaluru PropStack export (Dec 2022 – Nov 2025). Project-month absorption is allocated to track market inventory — not a PropStack project ledger. Not live KRERA unless <code>AURA_LIVE_*</code> is set.</p>
        </div>
        """
    )
