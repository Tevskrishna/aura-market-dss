"""
Executive AI Copilot — page-aware guide (rule + template).

Not a new ML model. Does not change launch scoring.
Answers product / metric / next-step questions with current Hub context.
"""
from __future__ import annotations

from typing import Any

from services.decision_brief_service import DECISION_JOURNEY, journey_index, next_after
from services.decision_context import get_decision_context

# Module → business question (first-time clarity)
MODULE_PURPOSE: dict[str, dict[str, str]] = {
    "Executive Hub": {
        "question": "Should we launch at this price?",
        "solves": "Gives the only final GO / HOLD / NO-GO for the open project.",
        "next": "Continue to Market Intelligence to check demand health.",
    },
    "Market Intelligence": {
        "question": "Is demand healthy?",
        "solves": "Shows absorption, inventory, and at-risk supply as market evidence.",
        "next": "Continue to Competition & Land.",
    },
    "Competition & Land": {
        "question": "Will competitors hurt us?",
        "solves": "Rival supply, RERA density, and land margin evidence for the Hub call.",
        "next": "Continue to Buyer Intelligence.",
    },
    "Buyer Intelligence": {
        "question": "Who will buy?",
        "solves": "Audience, channels, and booking behaviour.",
        "next": "Continue to Marketing Intelligence.",
    },
    "Marketing Intelligence": {
        "question": "Can marketing hit the target?",
        "solves": "SMC spend, ROI, and whether marketing can support the plan.",
        "next": "Continue to DMAIC Quality.",
    },
    "DMAIC Quality": {
        "question": "Why are problems occurring?",
        "solves": "Frames unsold inventory as a measurable defect (Define → Measure).",
        "next": "Continue to Project Deep Dive.",
    },
    "Project Deep Dive": {
        "question": "Is the project financially healthy?",
        "solves": "Builder / project absorption and forecast health.",
        "next": "Continue to Digital Twin.",
    },
    "Digital Twin": {
        "question": "What happens if strategy changes?",
        "solves": "What-if ₹ Cr outcomes for price, rival, and intervene.",
        "next": "Continue to Decision Explanation.",
    },
    "Decision Explanation": {
        "question": "Why did the Hub decide this?",
        "solves": "Evidence story behind the Hub call — not a second verdict.",
        "next": "Continue to SPC Control.",
    },
    "SPC Control": {
        "question": "Can we trust this decision?",
        "solves": "Statistical stability of demand velocity.",
        "next": "Continue to Reports for the board pack.",
    },
    "Reports": {
        "question": "What do we take to the board?",
        "solves": "Board decision pack locked to today’s Hub call.",
        "next": "Download PDF / HTML. Journey complete.",
    },
    "Map Intelligence": {
        "question": "Where should we build?",
        "solves": "Zone suitability evidence (optional drawer — not on main Continue chain).",
        "next": "Return to Hub or Competition for the launch call.",
    },
    "Demand Forecast": {
        "question": "What is the near-term outlook?",
        "solves": "Short-horizon demand forecast (optional drawer).",
        "next": "Return to Hub or SPC for trust checks.",
    },
}

METRIC_GLOSSARY: dict[str, str] = {
    "threat": (
        "**Launch Threat Score (0–100)** blends competition pressure, unsold inventory signal, "
        "twin ₹ Cr exposure, and margin viability. Higher = more risk. The Hub maps it to GO / HOLD / NO-GO."
    ),
    "absorption": (
        "**Absorption** is sold ÷ launched units. Healthy corridors usually sit higher; "
        "projects under ~70% are treated as at-risk inventory in this demo."
    ),
    "dpmo": (
        "**DPMO** (defects per million opportunities) treats unsold units as defects in a Six Sigma lens — "
        "capital locked in slow stock."
    ),
    "blind": (
        "**Blind-spot loss (₹ Cr)** estimates revenue at risk if a rival launches and you do not intervene. "
        "Directional twin output for IC discussion."
    ),
    "recovery": (
        "**Recovery (₹ Cr)** estimates what the intervene package (cut / subvention / timing) can claw back."
    ),
    "spc": (
        "**SPC / I-MR** checks whether booking or absorption velocity is statistically stable. "
        "Out-of-control points mean treat intervene plans with caution."
    ),
    "go": (
        "**GO / HOLD / NO-GO** is the only final launch recommendation and appears only on the Executive Hub. "
        "Other pages explain evidence or why — they do not replace it."
    ),
}


def _norm(q: str) -> str:
    return " ".join((q or "").lower().strip().split())


def answer_copilot(question: str, *, module: str | None = None) -> str:
    """Return a plain-language executive answer for the current page + Hub context."""
    q = _norm(question)
    mod = module or "Executive Hub"
    purpose = MODULE_PURPOSE.get(mod) or {
        "question": "How does this module help the launch call?",
        "solves": "Supports the Executive Hub decision with evidence.",
        "next": "Use Continue → or open Executive Hub.",
    }
    ctx = get_decision_context() or {}

    # Empty / greeting
    if not q or q in {"hi", "hello", "help", "?"}:
        return _intro(mod, purpose, ctx)

    if any(x in q for x in ("what is this", "what does this app", "what is realestate", "purpose of")):
        return (
            "**RealEstateIQ** is a Developer Decision Support System. "
            "It helps executives answer **Should we launch this project at this price?** "
            "with one Hub recommendation (GO / HOLD / NO-GO) and evidence modules that explain why."
        )

    if any(x in q for x in ("where should i start", "where do i start", "how do i start", "first step")):
        return (
            "Start on the **Executive Hub**. Select the project once, set ₹/sqft, read GO / HOLD / NO-GO, "
            "then press **Continue →**. Replay the product tour from the sidebar if you want the 2-minute overview."
        )

    if any(x in q for x in ("where next", "go next", "what next", "next step", "continue")):
        nxt = next_after(mod)
        if nxt:
            return (
                f"On **{mod}**, press **Continue → {nxt.label}**. "
                f"That step answers: *{nxt.reason}*"
            )
        return "You are at the end — download the **Reports** board pack."

    if any(x in q for x in ("for a ceo", "explain for ceo", "board language")):
        return (
            f"**CEO brief · {mod}**\n\n"
            f"**Decision question:** {purpose['question']}\n"
            f"**Why it matters:** {purpose['solves']}\n"
            f"**Do next:** {purpose['next']}\n\n"
            + _ctx_line(ctx)
            + "\nFinal launch call remains on **Executive Hub** only."
        )

    if any(x in q for x in ("sales head", "for sales", "sales manager")):
        return (
            f"**Sales Head brief · {mod}**\n\n"
            f"This page asks: *{purpose['question']}*\n"
            "Focus on absorption, price pressure, and which actions move bookings this fortnight.\n"
            f"**Next:** {purpose['next']}\n\n"
            + _ctx_line(ctx)
        )

    if any(x in q for x in ("simple", "eli5", "plain language", "in simple")):
        return (
            f"In plain terms: this screen helps you answer **{purpose['question']}**. "
            f"{purpose['solves']} The final launch call still lives only on the Executive Hub."
        )

    if any(x in q for x in ("summarize", "summary", "this page", "explain this page", "what does this module")):
        return (
            f"**{mod}** asks: *{purpose['question']}*\n\n"
            f"{purpose['solves']}\n\n"
            f"**Next:** {purpose['next']}"
        )

    if any(x in q for x in ("why go", "why hold", "why no", "why recommendation", "why is the recommendation")):
        return _why_hub(ctx)

    if any(x in q for x in ("risk high", "why risk", "threat high", "threat score")):
        return _risk_explain(ctx) + "\n\n" + METRIC_GLOSSARY["threat"]

    if "absorption" in q or "demand" in q:
        return METRIC_GLOSSARY["absorption"]
    if "dpmo" in q or "sigma" in q or "six sigma" in q:
        return METRIC_GLOSSARY["dpmo"]
    if "blind" in q or "cannibal" in q:
        return METRIC_GLOSSARY["blind"]
    if "recovery" in q or "intervene" in q:
        return METRIC_GLOSSARY["recovery"]
    if "spc" in q or "control chart" in q or "ooc" in q or "trust" in q:
        return METRIC_GLOSSARY["spc"]
    if any(x in q for x in ("go/hold", "no-go", "nogo", "verdict", "final decision")):
        return METRIC_GLOSSARY["go"]

    if any(x in q for x in ("demand decrease", "demand drop", "market slows", "if demand")):
        return (
            "If demand softens: check **Market** absorption and **SPC** stability, "
            "stress price/marketing on **Digital Twin**, then return to **Hub** and re-read GO / HOLD / NO-GO. "
            "Do not invent a second verdict on other pages."
        )

    if "chart" in q or "graph" in q or "metric mean" in q or "what does this metric" in q:
        return (
            f"On **{mod}**, charts answer: *{purpose['question']}*. "
            "Use ⓘ help tips under key KPIs for what / why / action. "
            "Ask me about a named metric (threat score, absorption, DPMO, blind-spot, SPC)."
        )

    if "how do i use" in q or "how to use" in q:
        return (
            f"1) Read the page question: *{purpose['question']}*. "
            f"2) Scan the evidence sheet. 3) {purpose['next']} "
            "Use the Copilot or product tour if anything is unclear."
        )

    if "duplicate" in q or "second recommendation" in q:
        return METRIC_GLOSSARY["go"]

    # Default: page purpose + context
    return (
        f"I’m your executive guide on **{mod}**.\n\n"
        f"**Business question:** {purpose['question']}\n"
        f"**Why you’re here:** {purpose['solves']}\n"
        f"**Do next:** {purpose['next']}\n\n"
        + _ctx_line(ctx)
        + "\nTry asking: *Why is risk high?* · *Where should I go next?* · *Summarize this page.*"
    )


def _intro(mod: str, purpose: dict[str, str], ctx: dict[str, Any]) -> str:
    idx = journey_index(mod)
    progress = ""
    if idx >= 0:
        progress = f" You are on step **{idx + 1} of {len(DECISION_JOURNEY)}**."
    return (
        f"Hello — I’m the **RealEstateIQ Copilot** on **{mod}**.{progress}\n\n"
        f"This page asks: **{purpose['question']}**\n\n"
        f"{purpose['solves']}\n\n"
        + _ctx_line(ctx)
        + "\nAsk me anything about metrics, the Hub call, or what to do next."
    )


def _ctx_line(ctx: dict[str, Any]) -> str:
    if not ctx:
        return "_No Hub project locked yet — open Executive Hub and set project + ₹/sqft._"
    return (
        f"**Open decision:** {ctx.get('project')} · Hub **{ctx.get('verdict')}** · "
        f"risk {ctx.get('threat_score')}/100 · ₹{ctx.get('my_price_psf', 0):,.0f}/sqft."
    )


def _why_hub(ctx: dict[str, Any]) -> str:
    if not ctx:
        return (
            "Lock a project on the **Executive Hub** first. "
            "Then I can explain why that GO / HOLD / NO-GO was shown."
        )
    v = str(ctx.get("verdict") or "—")
    return (
        f"The Hub called **{v}** on **{ctx.get('project')}** with threat **{ctx.get('threat_score')}/100**. "
        f"Blind-spot ≈ ₹{ctx.get('blind_spot_loss_cr')} Cr; recovery ≈ ₹{ctx.get('recovery_cr')} Cr. "
        "Open **Decision Explanation** for the evidence story. "
        "Other modules support this call — they do not replace it."
    )


def _risk_explain(ctx: dict[str, Any]) -> str:
    if not ctx:
        return "Open the Hub to compute today’s Launch Threat Score."
    score = int(ctx.get("threat_score") or 0)
    band = "elevated" if score >= 55 else ("moderate" if score >= 35 else "contained")
    return (
        f"Current Hub risk is **{score}/100** ({band}) for **{ctx.get('project')}**. "
        "Drivers typically include rival price pressure, UC unsold, twin exposure, and margin stress. "
        "See **Why this score** on the Hub and Competition / Twin for evidence."
    )


SUGGESTED_PROMPTS = [
    "What is this application?",
    "Where should I start?",
    "Summarize this page",
    "Why is the recommendation GO or HOLD?",
    "Why is risk high?",
    "Where should I go next?",
    "Explain this in simple language",
    "What happens if demand decreases?",
]
