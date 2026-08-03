"""
Scroll-triggered counters + chart draw-in.

Streamlit sandboxes markdown HTML; we inject a tiny bridge into the parent
document via components.html so IntersectionObserver can run on the real page.
"""
from __future__ import annotations

import streamlit as st
import streamlit.components.v1 as components

_BRIDGE_FLAG = "_iq_scroll_motion_injected"


def inject_scroll_motion(*, force: bool = False) -> None:
    """Re-inject each call so late-mounted charts get observed after lens switches."""
    _ = force
    st.session_state[_BRIDGE_FLAG] = True
    components.html(
        """
<script>
(function () {
  const doc = window.parent.document;
  if (!doc) return;

  function easeOut(t) {
    return 1 - Math.pow(1 - t, 3);
  }

  function formatValue(n, decimals, prefix, suffix) {
    const fixed = decimals > 0 ? n.toFixed(decimals) : Math.round(n).toString();
    const withCommas = fixed.replace(/\\B(?=(\\d{3})+(?!\\d))/g, ",");
    return (prefix || "") + withCommas + (suffix || "");
  }

  function runCounter(el) {
    if (el.dataset.counted === "1") return;
    el.dataset.counted = "1";
    const target = parseFloat(el.dataset.target || "0");
    const decimals = parseInt(el.dataset.decimals || "0", 10);
    const prefix = el.dataset.prefix || "";
    const suffix = el.dataset.suffix || "";
    const duration = parseInt(el.dataset.duration || "1400", 10);
    const start = performance.now();
    function tick(now) {
      const p = Math.min(1, (now - start) / duration);
      const val = target * easeOut(p);
      el.textContent = formatValue(val, decimals, prefix, suffix);
      if (p < 1) requestAnimationFrame(tick);
      else el.textContent = formatValue(target, decimals, prefix, suffix);
    }
    requestAnimationFrame(tick);
  }

  function playPlot(plot) {
    if (!plot || plot.dataset.iqPlayed === "1") return;
    const Plotly = window.parent.Plotly;
    plot.dataset.iqPlayed = "1";
    plot.classList.add("iq-plot-in");
    if (!Plotly) return;
    const frames = plot.frames || (plot._transitionData && plot._transitionData._frames) || [];
    if (!frames.length) return;
    try {
      Plotly.animate(plot, null, {
        frame: { duration: 95, redraw: true },
        transition: { duration: 75, easing: "cubic-in-out" },
        fromcurrent: false
      });
    } catch (e) {}
  }

  function observeAll() {
    const opts = { threshold: 0.22, rootMargin: "0px 0px -6% 0px" };
    const io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        const node = entry.target;
        if (node.classList.contains("st-snap") || node.classList.contains("st-count-root")) {
          node.classList.add("st-inview");
          node.querySelectorAll(".st-count").forEach(runCounter);
        }
        if (node.classList.contains("st-pt-wrap")) {
          node.classList.add("st-inview");
        }
        if (node.classList.contains("js-plotly-plot")) {
          playPlot(node);
        }
        io.unobserve(node);
      });
    }, opts);

    doc.querySelectorAll(".st-snap, .st-count-root, .st-pt-wrap, .js-plotly-plot").forEach(function (el) {
      if (el.dataset.iqObserved === "1") return;
      el.dataset.iqObserved = "1";
      // If already on screen (e.g. top of page), fire immediately
      const rect = el.getBoundingClientRect();
      const vh = window.parent.innerHeight || 800;
      if (rect.top < vh * 0.85 && rect.bottom > 40) {
        if (el.classList.contains("st-snap") || el.classList.contains("st-count-root")) {
          el.classList.add("st-inview");
          el.querySelectorAll(".st-count").forEach(runCounter);
        }
        if (el.classList.contains("st-pt-wrap")) el.classList.add("st-inview");
        if (el.classList.contains("js-plotly-plot")) playPlot(el);
      } else {
        io.observe(el);
      }
    });
  }

  observeAll();
  setTimeout(observeAll, 500);
  setTimeout(observeAll, 1200);
  setTimeout(observeAll, 2200);

  if (!window.parent.__iqMotionMO) {
    window.parent.__iqMotionMO = new MutationObserver(function () {
      clearTimeout(window.parent.__iqMotionT);
      window.parent.__iqMotionT = setTimeout(observeAll, 280);
    });
    window.parent.__iqMotionMO.observe(doc.body, { childList: true, subtree: true });
  }
})();
</script>
        """,
        height=0,
        width=0,
    )
