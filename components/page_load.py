"""Page-ready progress cue — honest load feedback (no fake 3D theater)."""
from __future__ import annotations

import html

import streamlit as st


def render_page_load_cue(module: str | None = None) -> None:
    """
    Thin top progress that fills once per page run, then marks Ready.
    Complements Streamlit's top-right running indicator.
    """
    label = html.escape(module or "Workspace")
    st.html(
        f"""
        <div class="iq-page-load" role="status" aria-live="polite" aria-label="Page load">
          <div class="iq-page-load-track" aria-hidden="true">
            <div class="iq-page-load-bar"></div>
          </div>
          <div class="iq-page-load-meta">
            <span class="iq-page-load-dot" aria-hidden="true"></span>
            <strong>Ready</strong>
            <span>{label} · charts zoom · layer buttons switch views</span>
          </div>
        </div>
        """
    )
