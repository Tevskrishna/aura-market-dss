# REPOSITORY_STRUCTURE.md — AURA-Market

**Generated:** 2026-07-20  
**Mode:** Read-only inventory (no application code modified)  
**Root:** `C:\Users\Admin\Projects\bagaluru-analytics-dss`  
**Remote:** https://github.com/Tevskrishna/aura-market-dss  

Companion document: [`PROJECT_AUDIT.md`](./PROJECT_AUDIT.md)

---

## How to read this file

1. **Folder responsibilities** — what that directory owns in the architecture.
2. **Complete tree** — every tracked project file (excluding `.git/` object store).
3. **Python file index** — one-line description for every `.py` file.

Ephemeral tooling caches (`.pytest_cache/`) are listed at the end and are not part of the product.

---

## Architecture snapshot (folders only)

```
UI          → app.py, pages/, components/, assets/
Logic       → services/, models/
Config      → config/, .streamlit/
Data        → data/, scripts/ (builders)
Charts      → utils/
Legacy      → src/  (superseded by services/; keep for reference debt)
Docs/Tests  → docs/, tests/, PROJECT_AUDIT.md, README.md, SCOPE.md
```

---

## Folder responsibilities

| Folder / path | Responsibility |
|---|---|
| `/` (root) | Entrypoint (`app.py`), dependency pins, product docs, audit artifacts |
| `.streamlit/` | Streamlit runtime theme (`config.toml` — dark base palette) |
| `assets/` | CSS theme + UI reference stills from accepted WhatsApp Map DSS video |
| `assets/ui_ref/` | Extracted reference frames (visual parity only; not used at runtime) |
| `components/` | Reusable Streamlit UI chrome (auth, KPI cards, filters, heroes) |
| `config/` | Settings, demo auth, dataset schema contracts |
| `data/` | Runtime CSV inputs (projects, competition seed, SMC, demographics, zones) |
| `docs/` | Architecture, demo script, known limitations, submission checklist |
| `models/` | Shared dataclasses / domain types (not ML weight files) |
| `pages/` | Streamlit multipage surfaces (one business module per file) |
| `scripts/` | Offline ETL / seed builders / submission validation CLI |
| `services/` | **Canonical business logic** — pages should call here, not reimplement |
| `src/` | **Legacy layer** — earlier implementation; largely superseded by `services/` |
| `tests/` | Pytest coverage for foundation + submission pack |
| `utils/` | Plotly chart builders / display formatters (presentation helpers) |
| `.pytest_cache/` | Pytest cache (generated; safe to delete) |

---

## Complete repository tree

```
bagaluru-analytics-dss/
├── .gitignore
├── .streamlit/
│   └── config.toml
├── PROJECT_AUDIT.md
├── README.md
├── SCOPE.md
├── REPOSITORY_STRUCTURE.md          ← this file
├── app.py
├── requirements.txt
├── requirements-dev.txt
├── assets/
│   ├── .gitkeep
│   ├── styles.css
│   └── ui_ref/
│       ├── extra_0.jpg
│       ├── extra_1.jpg
│       ├── extra_2.jpg
│       ├── frame_00.jpg
│       ├── frame_01.jpg
│       ├── frame_02.jpg
│       ├── frame_03.jpg
│       ├── frame_04.jpg
│       ├── frame_05.jpg
│       ├── frame_06.jpg
│       └── frame_07.jpg
├── components/
│   ├── __init__.py
│   ├── filters.py
│   ├── kpi_cards.py
│   └── layout.py
├── config/
│   ├── __init__.py
│   ├── auth.py
│   ├── schemas.py
│   └── settings.py
├── data/
│   ├── buyer_demographics.csv
│   ├── land_prices.csv
│   ├── lead_insights.csv
│   ├── lead_insights_README.txt
│   ├── marketing_spends.csv
│   ├── monthly_absorption.csv
│   ├── projects.csv
│   ├── rera_projects.csv
│   ├── smc_spends.csv
│   ├── under_construction.csv
│   ├── upcoming_projects.csv
│   └── zones.csv
├── docs/
│   ├── ARCHITECTURE.md
│   ├── AURA_SPEC.md
│   ├── DEMO_SCRIPT.md
│   ├── KNOWN_LIMITATIONS.md
│   ├── MARKET_OVERVIEW.md
│   └── SUBMISSION_CHECKLIST.md
├── models/
│   ├── README.md
│   ├── __init__.py
│   └── market.py
├── pages/
│   ├── 1_Market_Overview.py
│   ├── 2_Competition_Intelligence.py
│   ├── 3_Buyer_Analytics.py
│   ├── 4_Marketing_Intelligence.py
│   ├── 5_DMAIC_Workspace.py
│   ├── 6_Builder_Deep_Dive.py
│   ├── 7_Digital_Twin.py
│   ├── 8_AI_Recommendations.py
│   ├── 9_SPC_Control_Chart.py
│   ├── 10_Map_Decision_Support.py
│   ├── 11_Executive_Reports.py
│   └── 12_Forecasting.py
├── scripts/
│   ├── build_marketing_spends.py
│   ├── build_seed_data.py
│   ├── ingest_lead_insights.py
│   └── validate_submission.py
├── services/
│   ├── __init__.py
│   ├── adapters.py
│   ├── buyer_service.py
│   ├── competition_service.py
│   ├── data_loader.py
│   ├── data_validator.py
│   ├── dmaic_service.py
│   ├── filter_service.py
│   ├── map_service.py
│   ├── margin_service.py
│   ├── marketing_service.py
│   ├── market_service.py
│   ├── recommendation_engine.py
│   ├── report_service.py
│   ├── sigma_service.py
│   ├── spc_service.py
│   └── twin_service.py
├── src/
│   ├── __init__.py
│   ├── digital_twin.py
│   ├── loaders.py
│   ├── recommendations.py
│   ├── sigma_utils.py
│   ├── spc.py
│   └── suitability.py
├── tests/
│   ├── test_market_foundation.py
│   └── test_submission_pack.py
└── utils/
    ├── __init__.py
    ├── charts.py
    ├── dmaic_charts.py
    ├── formatting.py
    └── map_charts.py
```

### Non-product / generated (present on disk)

```
.pytest_cache/
├── .gitignore
├── CACHEDIR.TAG
├── README.md
└── v/cache/nodeids
```

---

## Non-Python file quick index

| Path | One-line role |
|---|---|
| `.gitignore` | Ignores venv, secrets, Excel scratch files, `__pycache__` |
| `.streamlit/config.toml` | Dark Streamlit theme + headless-friendly server defaults |
| `README.md` | Project orientation / how to run |
| `SCOPE.md` | Product/scope framing notes |
| `PROJECT_AUDIT.md` | Full architecture/completion audit (scores, gaps, ML, maps) |
| `requirements.txt` | Runtime deps (Streamlit, pandas, Plotly, Folium, sklearn, openpyxl) |
| `requirements-dev.txt` | Dev deps (pytest) |
| `assets/styles.css` | Dark enterprise UI stylesheet injected at runtime |
| `assets/.gitkeep` | Keeps empty assets folder in git when needed |
| `assets/ui_ref/*.jpg` | Visual reference frames from accepted Map DSS demo video |
| `data/*.csv` | Canonical local datasets loaded by adapters/services |
| `data/lead_insights_README.txt` | Notes on lead insights CSV provenance |
| `docs/ARCHITECTURE.md` | Intended layered architecture write-up |
| `docs/AURA_SPEC.md` | AURA-Market product specification notes |
| `docs/DEMO_SCRIPT.md` | Walkthrough script for mentors/company demo |
| `docs/KNOWN_LIMITATIONS.md` | Honest gap list (seed data, stubs, pseudo-labels) |
| `docs/MARKET_OVERVIEW.md` | Market overview module notes |
| `docs/SUBMISSION_CHECKLIST.md` | Pre-submission checklist |
| `models/README.md` | Clarifies `models/` = domain types, not saved ML weights |

### Data files (CSV)

| File | Role |
|---|---|
| `data/projects.csv` | Project inventory (absorption, price, builder attributes) |
| `data/monthly_absorption.csv` | Time series for SPC / forecast |
| `data/buyer_demographics.csv` | Booking-level audience fields |
| `data/lead_insights.csv` | Lead funnel / channel insights (curated from PDF) |
| `data/marketing_spends.csv` | Normalized SMC spend long-format (₹ Cr) |
| `data/smc_spends.csv` | Wider/rawer SMC share still lightly used |
| `data/rera_projects.csv` | **Seed** RERA approvals density |
| `data/upcoming_projects.csv` | **Seed** coming-soon competition |
| `data/under_construction.csv` | **Seed** UC competing stock |
| `data/land_prices.csv` | Land cost inputs for margin index |
| `data/zones.csv` | 25 Bengaluru zones for Map DSS |

---

## Every Python file — one-line description

### Root

| File | Description |
|---|---|
| `app.py` | Home page: login gate, product framing, dataset readiness, module navigation cards |

### `components/` — UI only

| File | Description |
|---|---|
| `components/__init__.py` | Package marker for UI components |
| `components/layout.py` | Theme injection, demo auth gate, sidebar chrome, heroes, section labels, module cards |
| `components/kpi_cards.py` | Responsive HTML KPI strip + buyer distribution progress rows |
| `components/filters.py` | Global filter bar (project, builder, date range, quarter) |

### `config/` — configuration contracts

| File | Description |
|---|---|
| `config/__init__.py` | Package marker for configuration |
| `config/settings.py` | Single source of truth for paths, thresholds, brand strings, chart defaults |
| `config/auth.py` | Demo username/password verification for walkthroughs |
| `config/schemas.py` | Expected column contracts consumed by the data validator |

### `models/` — domain types

| File | Description |
|---|---|
| `models/__init__.py` | Package marker for domain models |
| `models/market.py` | Dataclasses shared across market, competition, DMAIC, twin, and forecast flows |

### `pages/` — Streamlit surfaces (one module each)

| File | Description |
|---|---|
| `pages/1_Market_Overview.py` | Bagaluru scorecard: units, absorption bands, sigma/DPMO, price dynamics |
| `pages/2_Competition_Intelligence.py` | RERA / upcoming / UC / land tabs + Developer Margin Viability Index |
| `pages/3_Buyer_Analytics.py` | Audience demographics: age, native/outstation, family, channels |
| `pages/4_Marketing_Intelligence.py` | SMC spend vs bookings/sales efficiency views |
| `pages/5_DMAIC_Workspace.py` | DEFINE/MEASURE shell: defect framing, CTQs, Pareto, at-risk list |
| `pages/6_Builder_Deep_Dive.py` | Per-builder KPIs, sold/unsold stack, GB absorption forecast, causes |
| `pages/7_Digital_Twin.py` | Rival cannibalization + price/subvention intervention simulator |
| `pages/8_AI_Recommendations.py` | Rule/ML recommendation list with WHY + mini twin preview |
| `pages/9_SPC_Control_Chart.py` | Six Sigma I-MR charts + Western Electric-style runs + short forecast |
| `pages/10_Map_Decision_Support.py` | 25-zone suitability map DSS (Folium/Plotly tabs: radar, compare, what-if) |
| `pages/11_Executive_Reports.py` | Downloadable markdown decision brief for mentors/company |
| `pages/12_Forecasting.py` | Short-horizon sales/absorption outlook with confidence bands |

### `services/` — canonical business logic

| File | Description |
|---|---|
| `services/__init__.py` | Package marker for services |
| `services/adapters.py` | Data source adapters (local CSV today; live API stub for KRERA/land later) |
| `services/data_loader.py` | Central load of validated catalog DataFrames |
| `services/data_validator.py` | Schema validation helpers with no I/O |
| `services/filter_service.py` | Filter option discovery and application to frames |
| `services/market_service.py` | Market Overview KPI and chart-ready aggregates |
| `services/sigma_service.py` | Absorption, DPMO, sigma level, ML sample augmentation helpers |
| `services/competition_service.py` | Mentor’s four competition asks as structured frames |
| `services/margin_service.py` | Land arbitrage + Developer Margin Viability Index |
| `services/buyer_service.py` | Audience/lead demographic aggregations |
| `services/marketing_service.py` | SMC spend efficiency aggregates (currently under-using full SMC width) |
| `services/dmaic_service.py` | DMAIC DEFINE/MEASURE hooks and at-risk framing |
| `services/recommendation_engine.py` | GB absorption forecast + rule-based actionable recommendations |
| `services/twin_service.py` | Segmented twin with competitive cannibalization and interventions |
| `services/spc_service.py` | I-MR control limits, runs signals, linear+seasonal forecast helper |
| `services/map_service.py` | Zone feature engineering, suitability scoring, metro overlay, what-if |
| `services/report_service.py` | Assembles executive markdown brief from shared services |

### `utils/` — presentation helpers

| File | Description |
|---|---|
| `utils/__init__.py` | Package marker for utilities |
| `utils/charts.py` | Dark-theme Plotly builders for core market/booking charts |
| `utils/dmaic_charts.py` | Phase-1 DMAIC/market Plotly visuals (bands, twin curves, I-MR) |
| `utils/map_charts.py` | Map DSS Plotly helpers (radar, price bars, heatmap, importance) |
| `utils/formatting.py` | Display formatters for KPI values (no business logic) |

### `scripts/` — offline builders / gates

| File | Description |
|---|---|
| `scripts/build_seed_data.py` | Generates seed CSVs and ingests booking Excels into project datasets |
| `scripts/build_marketing_spends.py` | Normalizes SMC Spends Working File → `marketing_spends.csv` |
| `scripts/ingest_lead_insights.py` | Builds structured `lead_insights.csv` (PDF may be image-only) |
| `scripts/validate_submission.py` | CLI readiness check to run before demos/submission |

### `tests/`

| File | Description |
|---|---|
| `tests/test_market_foundation.py` | Unit tests for Market Overview foundation services |
| `tests/test_submission_pack.py` | Broader AURA-Market / submission-pack regression tests |

### `src/` — legacy (technical debt; prefer `services/`)

| File | Description |
|---|---|
| `src/__init__.py` | Legacy package marker |
| `src/loaders.py` | Older CSV loaders (superseded by `services/data_loader` + adapters) |
| `src/sigma_utils.py` | Older sigma/absorption helpers (superseded by `sigma_service`) |
| `src/recommendations.py` | Older recommendation rules (superseded by `recommendation_engine`) |
| `src/digital_twin.py` | Older twin entrypoints (superseded by `twin_service`) |
| `src/spc.py` | Older SPC helpers (superseded by `spc_service`) |
| `src/suitability.py` | Older zone suitability helpers (superseded by `map_service`) |

---

## Python file count

| Area | Count |
|---|---|
| Root | 1 |
| components | 4 |
| config | 4 |
| models | 2 |
| pages | 12 |
| services | 17 |
| utils | 5 |
| scripts | 4 |
| tests | 2 |
| src (legacy) | 7 |
| **Total `.py` files** | **58** |

---

## Notes aligned to Version-2 freeze questions

| Concern | Where it shows up in this tree |
|---|---|
| Scalability / duplication | Parallel `src/` + `services/`; some page logic still orchestration-heavy |
| Seed competition data | `data/rera_projects.csv`, `upcoming_projects.csv`, `under_construction.csv`, `land_prices.csv` |
| SMC underused | `data/smc_spends.csv` present; primary path is thinner `marketing_spends.csv` via `marketing_service.py` |
| Production readiness | CSV-only `data/`, demo `config/auth.py`, no DB/logging package, sparse `tests/` |
| Decision-support gap (“what should developer do?”) | Strongest intent in `pages/7_*`, `pages/8_*`, `recommendation_engine.py`, `report_service.py` — still uneven across other pages |

---

*End of REPOSITORY_STRUCTURE.md — generated for architecture review before Version 2.*
