# RealEstateIQ — Enterprise Product Plan & Gap Analysis

**Planning status:** COMPLETE — **P0 implementation STARTED 2026-07-20**  
**Codebase under review:** AURA-Market (`bagaluru-analytics-dss`)  
**Target product name:** **RealEstateIQ** — *AI-Powered Real Estate Decision Intelligence Platform*  
**Branding rule (agreed):** Keep AURA-Market code/repo for now; all planning uses RealEstateIQ. Rebrand is a controlled Phase item, not a big-bang rewrite.  
**Date:** 2026-07-20  
**Companion docs:** `PROJECT_MASTER_REVIEW.md`, `docs/ARCHITECTURE.md`, `docs/KNOWN_LIMITATIONS.md`, `docs/CHANGELOG.md`

---

# 1. Enterprise Product Vision

## 1.1 One sentence
RealEstateIQ is a **decision OS** for Indian residential developers — every screen answers *what happened / why / what will happen / what should we do / what if we change X*.

## 1.2 Not this / yes this

| Not | Yes |
|---|---|
| Chart gallery / college DMAIC demo | Production SaaS Decision Support System |
| 12 peer Streamlit pages of equal weight | Role-based hubs around **business questions** |
| Seed CSVs presented as “live market” | Honest data contracts + live adapters when ready |
| “AI” as decoration | Prediction + risk + recommendation with confidence + audit trail |
| Streamlit demo passwords | Tenant SSO, RBAC, environments |

## 1.3 Target users → primary questions

| User | Primary question RealEstateIQ must answer |
|---|---|
| CEO / Investor | Should we launch / buy land / hold cash this quarter? |
| COO / Strategy | What is our pipeline risk if rivals and rates move? |
| Land team | Is this parcel viable after FSI, competition, and exit price? |
| Sales | What price and mix clears inventory? |
| Marketing | Where does the next ₹ Cr of SMC produce bookings? |
| Project managers | What delay does to absorption and margin? |

## 1.4 Product principle (non-negotiable)
**If a chart does not change a decision, it does not ship.**

## 1.5 North-star experience
1. Open RealEstateIQ → **Executive Decision Hub**  
2. See GO / HOLD / NO-GO on launch & land  
3. Drill into evidence (market, competition, buyers, $)  
4. Run **what-if** twin  
5. Export board pack  

The current Launch Co-pilot is the embryo of this hub — preserve and elevate it; do not bury it under 16 peer modules.

## 1.6 Brand transition
| Now (code) | Target (product) |
|---|---|
| AURA-Market | RealEstateIQ |
| Demo Streamlit Cloud | Tenant SaaS (`app.realestateiq…`) |
| Bagaluru-only seed | Multi micro-market (Bagaluru first) |

---

# 2. Current Architecture (as-built)

## 2.1 Runtime shape
```
Streamlit UI (app.py + pages/* + components/* + assets CSS)
        ↓
Services (business logic) — launch_copilot, market, competition, twin, map, …
        ↓
Adapters (LocalCatalogAdapter | LiveApiAdapter stub)
        ↓
data_loader DataCatalog @lru_cache  →  CSV files
```

## 2.2 What already matches enterprise intent

| Strength | Evidence |
|---|---|
| Service-layer intent | Pages call `services/*`; CSV reads not supposed to live in pages |
| Adapter seam | `services/adapters.py` ready for live swap |
| Decision wedge | Launch Co-pilot GO/HOLD/NO-GO + Threat Score |
| Domain coverage skeleton | Market, competition, buyer, marketing, twin, map, DMAIC, SPC, reports |
| Tests (thin) | Foundation + submission + copilot |
| Dark theming + photoreal heroes | `assets/*`, `components/media.py` |

## 2.3 Layers vs Desired clean architecture

| Desired | Current | Gap |
|---|---|---|
| UI | Streamlit pages + HTML/CSS | Pages still orchestrate heavily |
| Business | Partially in services | Some rules/UI mixed; no pure domain package |
| Services | Yes | Good starting point |
| Repositories | **Missing** | Catalog/adapter act as ad-hoc repo |
| Models | Dataclasses only | No ORM; no persistence models |
| DB | CSV | SQLite/Postgres not present |
| Config | `config/settings.py` | Env/secrets incomplete |
| Logging | Minimal | No structured logging |
| Auth | Demo dict | Not enterprise |

## 2.4 Module map (current → desired RealEstateIQ names)

| Desired module | Current surface | Maturity |
|---|---|---|
| Executive Dashboard | `app.py` Co-pilot (partial) | Medium |
| Market Intelligence | `1_Market_Overview` | Medium |
| Competition Intelligence | `2_*` | Medium (seed) |
| Project Intelligence | `6_Builder_Deep_Dive` | Medium |
| Buyer Intelligence | `3_*` | Medium |
| Pricing Intelligence | Scattered (Co-pilot, twin, margin) | Low as module |
| Marketing Intelligence | `4_*` | Medium |
| Land Intelligence | Tab inside competition + margin | Low |
| RERA Intelligence | Competition tab | Low (seed) |
| Upcoming Projects | Competition tab | Low (seed) |
| AI Recommendations | `8_*` | Medium-low |
| Demand Forecasting | `12_*` + SPC | Medium-low |
| Digital Twin | `7_*` | Medium (NumPy not SimPy) |
| DMAIC | `5_*` + SPC `9_*` | Medium (ANALYZE thin) |
| Reports | `11_*` | Medium |
| Administration | **Missing** | None |

---

# 3. Gap Analysis

## 3.1 Strengths (keep)
1. Clear business problem (competition blind spot + unsold as defect).  
2. Service-oriented folder discipline better than most demos.  
3. Launch Co-pilot = productizable decision moment.  
4. Twin framing (₹ Cr loss / recovery) speaks executive language.  
5. Real booking/SMC Excel lineage (not only fake data).  

## 3.2 Weaknesses
1. Streamlit multipage IA reads as college dashboard, not SaaS.  
2. Competition/land/upcoming are **seeds** presented with production tone.  
3. Map RF is **circular / pseudo-labeled**.  
4. Twin is illustrative NumPy, not SimPy production sim.  
5. No repository/DB layer; no migrations; no multi-tenant.  
6. Auth is plaintext demos in source.  
7. UI inconsistent (Co-pilot vs older pages); login deep-link trap.  
8. Mobile not enterprise-grade despite CSS patches.  
9. ML stack incomplete vs vision (no XGBoost/LightGBM/Prophet yet; no anomaly detection as product).  
10. AgGrid / light mode / design system tokens incomplete.  

## 3.3 Architecture risks
| Risk | Impact |
|---|---|
| Big-bang rewrite to “RealEstateIQ” | Destroy working demo value |
| Adding 16 peer pages | UX regression; “museum of charts” |
| Calling seed data “live” | Trust collapse with CEO buyers |
| Fitting more ML without labels | Worse than rules |
| Streamlit as forever UI | Ceiling vs Fabric/Power BI/ArcGIS expectations |

## 3.4 Capability gap matrix (Desired vs Current)

| Business question | Desired | Current | Gap severity |
|---|---|---|---|
| Buy this land? | Land DSS + margin + comps | Land tab + margin index | **High** |
| Launch now? | Co-pilot calibrated | Co-pilot (unvalidated weights) | Medium |
| Apartment mix? | Mix optimizer | Buyer unit mix only | **High** |
| Launch price? | Pricing module | Sliders + twin | Medium |
| Top competitor? | Ranked rivalry graph | Upcoming table / threat | Medium |
| Demand up? | Forecast + drivers | Short polyfit/sine | **High** |
| Price up what-if? | Twin scenario pack | Twin price cut path | Medium |
| Unsold inventory? | Risk bands + forecast | Absorption/sigma | Medium |
| Marketing budget? | MROI optimizer | ROI quartiles / reallocate tips | Medium |
| Expected profit? | Full P&L bridge | Margin % heuristic | **High** |

---

# 4. UI/UX Improvement Plan

## 4.1 Design system (build once, reuse everywhere)
Create `components/design_system/`:
- Tokens: color (light/dark), spacing 4/8/12/16/24, radius, elevation  
- Primitives: Button, Card, Metric, EmptyState, ErrorState, LoadingSkeleton  
- Data: FilterBar, DataTable (AgGrid), ExportBar  
- Charts: themed Plotly factory  
- Maps: MapShell (Folium/Leaflet wrapper)  

**Rule:** No page-only one-off cards when a primitive exists.

## 4.2 Information architecture (kill the museum)
```
RealEstateIQ
├── Executive Hub          ← elevate Co-pilot
├── Intelligence
│   ├── Market
│   ├── Competition (RERA / Upcoming / UC)
│   ├── Buyers
│   └── Land
├── Operations
│   ├── Projects
│   ├── Pricing
│   └── Marketing
├── Decisions
│   ├── Recommendations
│   ├── Simulation (Twin)
│   └── Forecast
├── Quality
│   └── DMAIC + SPC
├── Reports
└── Admin
```
Sidebar shows **≤7 top items**; rest nested. Roles hide modules.

## 4.3 Visual bar (inspiration with discipline)
Power BI / Fabric / ArcGIS Dashboard / Bloomberg density **selectively** — not cloned chrome.  
Photos for land/project context; never empty charcoal panels as “brand.”

## 4.4 Enterprise UI checklist (definition of done per page)
- Loading / empty / error states  
- Filters sticky  
- Export  
- Decision callout (“what should we do”)  
- Responsive breakpoints  
- Contrast AA  
- 44px tap targets  

## 4.5 Light + dark
Tokenized themes in CSS variables; Streamlit theme + custom CSS both driven from tokens.

---

# 5. Mobile Responsiveness Plan

## 5.1 Breakpoints (required)
320 · 375 · 768 · 1024 · 1440 · 1920

## 5.2 Behaviors
| Breakpoint | Layout |
|---|---|
| <768 | Sidebar collapsed; Modules/Hub select; cards 1-col; tables → card rows or horizontal scroll **inside table only** (page never overflows) |
| 768–1024 | 2-col KPI; map half height |
| ≥1024 | Full hub + evidence split |
| ≥1920 | Max content width ~1440–1600 centered |

## 5.3 Map/mobile
Map filters on-canvas (already started); never only-in-sidebar.  
Folium height scales (`min(380, 55vh)`).

## 5.4 Reality check
Streamlit **cannot** equal native Android/iPhone apps. Plan:
- Phase A: excellent responsive web  
- Phase B: PWA wrapper  
- Phase C (optional): React Native shell calling same APIs once backend exists  

## 5.5 Performance targets (from brief)
| Target | Approach |
|---|---|
| Startup <5s | Cache catalog; defer heavy ML; slim base64 heroes or CDN |
| Transition <500ms | Avoid full retrain; `st.cache_data`; pagination |
| Large data | AgGrid pagination; never dump 100k rows |

---

# 6. Business Feature Roadmap

| Phase | Business outcomes |
|---|---|
| **B0** | Honest labeling of seed data; Co-pilot as Executive Hub |
| **B1** | Land buy decision sheet (margin + rivalry + exit price) |
| **B2** | Pricing recommendation pack (launch price bands) |
| **B3** | Marketing budget allocator (MROI → weekly plan) |
| **B4** | Mix advisor (BHK mix vs demand) |
| **B5** | Board pack PDF that CEOs forward without apology |
| **B6** | Multi-project portfolio heat (CEO view) |

Every epic maps to a question in the brief — no orphan charts.

---

# 7. AI Roadmap

| Stage | Capability | Data prerequisite | Notes |
|---|---|---|---|
| A0 | Rules + Co-pilot score (existing) | Current CSVs | Keep; document weights |
| A1 | Persist GB absorption model + calibration | Projects history | Replace click-train |
| A2 | XGBoost/LightGBM absorption & price models | ≥3–5 yrs sell-through | Hold until data |
| A3 | Prophet / hierarchical demand forecast | Monthly series quality | Optional |
| A4 | Anomaly detection on I-MR + bookings | Stable SPC series | Surface as alerts |
| A5 | Buyer segmentation (clustering) | Demographics | Actionable segments only |
| A6 | Recommendation engine v2 (constraints + ROI) | Marketing + inventory | Unify with Co-pilot |
| A7 | Map suitability with **external labels** | Zone outcomes | Kill circular RF |

**Hard rule:** No new model ships without offline metric + confidence display + fallback rule.

**Simulation:** Move twin toward **SimPy** only when package/runtime stable on target Python; until then keep NumPy engine behind a `SimulationEngine` interface (adapter pattern).

---

# 8. Implementation Roadmap (incremental — no big bang)

> **Absolute rule:** Do not rewrite the repository. Extend services, preserve APIs, one module at a time.

### Wave 0 — Freeze & align (docs only → then tiny safe changes)
- Adopt RealEstateIQ plan as North Star  
- Mark seed datasets in UI copy  
- Fix deep-link login trap (redirect)  
- Design-system skeleton (tokens only)  

### Wave 1 — Executive Hub polish
- Elevate Co-pilot as “Executive Dashboard”  
- Collapse sidebar IA  
- Empty/loading/error primitives  

### Wave 2 — Repository + SQLite (dev)
- Introduce `repositories/` reading CSV first, then SQLite  
- Postgres-ready interfaces (`Protocol` / ABC)  
- No page SQL  

### Wave 3 — Competition / Land truthfulness
- Upgrade adapters; optional file drop zone for client Excel  
- Separate RERA / Upcoming / Land pages **or** clear sub-nav — without deleting old routes  

### Wave 4 — Pricing + Marketing decision packs
- New thin pages calling existing services + new pricing service  

### Wave 5 — Twin interface + scenario presets
- `SimulationEngine` ABC; NumPy impl; SimPy optional  

### Wave 6 — Reports enterprise
- PDF (WeasyPrint/ReportLab), Excel, CSV; templates  

### Wave 7 — Admin / tenancy / SSO (enterprise gate)
- Replace demo auth; audit log; feature flags  

### Wave 8 — Optional React shell
- Only if Streamlit UX ceiling blocks paid pilots  

---

# 9. Technical Roadmap

| Workstream | Actions |
|---|---|
| Architecture | UI → services → repositories → DB; no business logic in pages |
| Data | SQLite migrate scripts; Postgres Docker compose for staging |
| ML | Model registry folder `models/artifacts/`; train offline scripts |
| Maps | GeoJSON assets; cluster layer; documented CRS |
| Observability | `structlog` / standard logging; correlation IDs per session |
| Security | Secrets via env; hashed passwords or SSO; no secrets in repo |
| Quality | Expand pytest; contract tests for adapters; CI on GitHub Actions |
| DevOps | Staging Streamlit + optional FastAPI later; healthchecks |
| Docs | Data dictionary, module docs, changelog, release notes |

**Non-goals for next 90 days:** full rewrite, native apps, nationwide CoStar clone.

---

# 10. Final Priority Matrix

Impact × Effort (next actions). **P0 before any large feature build.**

| ID | Item | Impact | Effort | Priority | Depends on | **Status 2026-07-20** |
|---|---|---|---|---|---|---|
| P0-1 | Seed-data honesty labels in UI | High | Low | **P0** | — | **DONE** |
| P0-2 | IA: Executive Hub first; nest modules | High | Med | **P0** | Product freeze | **DONE** (5 nav sections) |
| P0-3 | Login deep-link redirect fix | Med | Low | **P0** | — | **DONE** |
| P0-4 | Design tokens + Metric/Empty/Error | High | Med | **P0** | — | **DONE** |
| P0-5 | Repository interface over catalog | High | Med | **P0** | — | **DONE** (lite) |
| P1-1 | Responsive table/map pass 320–1920 | High | Med | **P1** | P0-4 | **DONE** |
| P1-2 | Land decision sheet | High | Med | **P1** | P0-5 | **DONE** |
| P1-3 | Persist ML artifacts + no click-train | Med | Med | **P1** | Data | **DONE** |
| P1-4 | Marketing allocator v1 | High | Med | **P1** | P0-5 | **DONE** |
| P1-5 | PDF board pack | High | Med | **P1** | Hub | **DONE** (+ Hub Section 0) |
| P2-1 | SQLite + Postgres path | High | High | **P2** | P0-5 | SQLite mirror optional; Postgres later |
| P2-2 | Live adapter (KRERA/partner) | Very High | High | **P2** | Credentials | **BLOCKED** on credentials |
| P2-3 | SimPy engine behind interface | Med | High | **P2** | Twin ABC | ABC **DONE**; SimPy impl deferred |
| P2-4 | AgGrid everywhere tables | Med | Med | **P2** | P0-4 | Deferred |
| P2-5 | Light mode parity | Med | Med | **P2** | Tokens | Deferred |
| P3-1 | SSO / Admin module | Very High | High | **P3** | Tenancy | Deferred |
| P3-2 | Prophet / LightGBM suite | Med | High | **P3** | Labels | Deferred |
| P3-3 | React shell (if needed) | High | Very High | **P3** | API | Deferred |

**Demo / interview close-out:** see `docs/DEMO_100.md` — P0+P1 + Board Mode + SimulationEngine NumPy = **requirement-complete for mentor SCOPE** without claiming live government data.

---

# Decision Gate — When coding may start

Implementation begins **only** after stakeholders accept this plan and pick the first P0 slice.

**Recommended first implementation slice (when approved):**  
`P0-1 + P0-3 + P0-4 (tokens/empty/error) + P0-2 (nav collapse)` — preserve all features; no renames of services; no DB migration yet.

**Explicitly deferred until asked:**  
RealEstateIQ repo rename, Streamlit→React rewrite, deleting pages, SimPy forced migration, claiming live RERA.

---

# Appendix A — Current vs Desired stack

| Layer | Desired | Current | Plan |
|---|---|---|---|
| Frontend | Streamlit modular + AgGrid + responsive | Streamlit + Plotly + Folium | Add AgGrid + DS; optional React later |
| Backend | Services + repos | Services + adapter | Add repos |
| DB | SQLite → Postgres | CSV | Wave 2 |
| ML | sklearn + XGB/LGBM + Prophet | sklearn only | Stage A1–A3 |
| Sim | SimPy | NumPy twin | Interface first |
| Maps | OSM + GeoJSON + clustering | Folium points | Extend |
| Auth | SSO | Demo | Wave 7 |

---

# Appendix B — Every page must answer

For RealEstateIQ definition of done:

1. **What happened?** (KPIs / trends)  
2. **Why?** (drivers / competition / mix)  
3. **What will happen?** (forecast / twin)  
4. **What should we do?** (actions)  
5. **What if we change X?** (controls → regenerate)  

Pages that cannot support (4) and preferably (5) are **evidence drawers**, not home.

---

*End of planning document. No application source was modified to produce this plan. Implementation awaits explicit go-ahead on the recommended P0 slice.*
