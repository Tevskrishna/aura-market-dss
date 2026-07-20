"""
Journey UX metadata — labels, ETA, purpose copy.
UI-only. Does not touch scoring / engines / repositories.
"""
from __future__ import annotations

# Minutes remaining from this step (inclusive of remaining journey)
JOURNEY_ETA_MIN: dict[str, int] = {
    "Executive Hub": 10,
    "Market Intelligence": 9,
    "Competition & Land": 8,
    "Buyer Intelligence": 7,
    "Marketing Intelligence": 6,
    "DMAIC Quality": 5,
    "Project Deep Dive": 4,
    "Digital Twin": 3,
    "Decision Explanation": 2,
    "SPC Control": 1,
    "Reports": 1,
}

# Rich purpose strip per module
PAGE_PURPOSE: dict[str, dict[str, str]] = {
    "Executive Hub": {
        "why": "This is the only place the launch call is made.",
        "question": "Should we launch this project?",
        "outcome": "GO / HOLD / NO-GO with risk, impact, and actions.",
        "supports": "Final decision — every later page only explains or validates it.",
    },
    "Market Intelligence": {
        "why": "Demand health must support a launch.",
        "question": "Is market demand strong enough?",
        "outcome": "Absorption, inventory, and at-risk supply as evidence.",
        "supports": "Shows whether the Hub call is backed by corridor demand.",
    },
    "Competition & Land": {
        "why": "Rivals and land cost change launch risk.",
        "question": "Can competitors affect our launch?",
        "outcome": "Supply pressure and land margin evidence.",
        "supports": "Explains competition / land risk behind the Hub call.",
    },
    "Buyer Intelligence": {
        "why": "A launch needs a reachable buyer.",
        "question": "Who will buy this project?",
        "outcome": "Audience, channels, and booking behaviour.",
        "supports": "Confirms who the Hub plan is selling to.",
    },
    "Marketing Intelligence": {
        "why": "SMC must be able to hit the commercial target.",
        "question": "Can marketing achieve the sales target?",
        "outcome": "Spend, ROI, and allocation evidence.",
        "supports": "Shows whether marketing can execute the Hub plan.",
    },
    "DMAIC Quality": {
        "why": "Unsold inventory must be framed as a measurable problem.",
        "question": "What is causing this business problem?",
        "outcome": "Define / Measure view of defects and at-risk stock.",
        "supports": "Operational evidence for why Hub may HOLD or intervene.",
    },
    "Project Deep Dive": {
        "why": "Brand and project health concentrate capital risk.",
        "question": "Is this project financially healthy?",
        "outcome": "Absorption, forecast, and at-risk project evidence.",
        "supports": "Financial validation under the Hub call.",
    },
    "Digital Twin": {
        "why": "Strategy changes must be priced in ₹ Cr before print.",
        "question": "What happens if strategy changes?",
        "outcome": "What-if revenue, blind-spot, and recovery paths.",
        "supports": "Simulation evidence for Hub intervene choices.",
    },
    "Decision Explanation": {
        "why": "Leaders need the story behind the Hub call — not a second verdict.",
        "question": "Why did AI recommend this?",
        "outcome": "Evidence stack that supports the Hub decision.",
        "supports": "Explains why — never replaces GO / HOLD / NO-GO.",
    },
    "SPC Control": {
        "why": "Unstable velocity undermines any launch plan.",
        "question": "Can we trust these insights?",
        "outcome": "Statistical stability / OOC signals.",
        "supports": "Confidence check before the board pack.",
    },
    "Reports": {
        "why": "Leadership needs one board story, not another dashboard.",
        "question": "Executive decision pack",
        "outcome": "Board pack locked to today’s Hub call.",
        "supports": "Closes the journey with exportable narrative.",
    },
}
