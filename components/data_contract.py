"""Always-visible measured / seed / simulated data contract — Hub trust strip."""
from __future__ import annotations

import streamlit as st


def render_data_contract(*, compact: bool = False) -> None:
    """Enterprise honesty — first thing a CTO/CEO should see."""
    if compact:
        st.caption(
            "**Data contract:** Measured bookings/SMC · Seed competition/land · "
            "Simulated scenario ₹ Cr · Illustrative map (if opened). Not live KRERA unless configured."
        )
        return
    st.html(
        """
        <div class="iq-data-contract" role="note" aria-label="Data contract">
          <div class="iq-data-contract-kicker">Data contract · Bagaluru Aerospace Highway pilot</div>
          <div class="iq-data-contract-grid">
            <div><span>Measured</span><strong>Bookings · SMC spend</strong></div>
            <div><span>Seed / curated</span><strong>RERA · UC · upcoming · land indices</strong></div>
            <div><span>Simulated</span><strong>Scenario engine ₹ Cr (directional)</strong></div>
            <div><span>Illustrative</span><strong>Map suitability (Quality Lab)</strong></div>
          </div>
          <p>Not a live government RERA feed unless <code>AURA_LIVE_*</code> is configured. Speak this in the first 20 seconds of any IC demo.</p>
        </div>
        """
    )
