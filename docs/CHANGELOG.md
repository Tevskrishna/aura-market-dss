# Changelog

## 2026-07-20 — DEMO 100% requirement close-out

### Added
- `services/simulation_engine.py` — SimulationEngine ABC + NumpySimulationEngine (Wave 5)
- Board Mode sidebar toggle (presentation density)
- `weekly_actions_unified` — Hub Do-this-week merges co-pilot + prescribe lines
- `docs/DEMO_100.md` — P0/P1 status matrix + interview definition of done
- Tests: `tests/test_demo_100.py`

### Changed
- Hub / Twin / Recs run twin via `get_simulation_engine()`
- Enterprise plan §10 status column updated

## 2026-07-20 — Cinematic gate (RealEstateIQ entrance)

### Changed
- Login gate rebuild: RealEstateIQ brand hero, layered 3D photo stage, glass sign-in, Living Enterprise calm (not arcade)

## 2026-07-20 — Living Enterprise UI

### Changed
- Softened Race HUD into calm enterprise telemetry (`realtime_hud.css`) — no arcade infinite loops; `prefers-reduced-motion`
- Honest relative freshness (`format_relative_age`) on Hub / EDS / Twin / Reports
- Continuity toasts: Hub lock, Twin preset, Reports Hub-match
- Wired empty/error states on Market, Twin, Reports; skeleton helper
- Quiet one-shot KPI settle motion

### Docs
- `docs/IMPLEMENTATION_SUMMARY_LIVING_ENTERPRISE.md`

## 2026-07-20 — Realtime Race HUD (visual OS)

### Changed
- New `assets/realtime_hud.css` — NFS/GTA-inspired decision HUD (asphalt night, amber/cyan telemetry, live pulses, cinematic Hub + EDS)
- Typography: Exo 2 + Rajdhani (drop Inter)
- Hub live strip + mission title card; EDS open-decision telemetry strip
- Theme inject order includes HUD skin last

## 2026-07-20 — CEO Morning Loop (Decision OS)

### Added
- `services/decision_context.py` — Hub → Twin / Recs / Reports session continuity
- Board pack **Section 0. Open Decision** from live Hub `evaluate_launch` context
- Twin scenario presets (Blind spot / Intervene / Hold) + NumPy honesty
- `NAV_SECTIONS` sidebar grouping (≤5 sections, same 13 routes)
- Compact `page_hero` for morning-loop surfaces
- Tests: `tests/test_ceo_morning_loop.py`
- Docs: `docs/IMPLEMENTATION_SUMMARY_CEO_MORNING_LOOP.md`, updated `docs/DEMO_SCRIPT.md`

## 2026-07-20 — CTO Wave 1: Executive Decision Sheet

### Added
- Shared `DecisionBrief` model + adapters (launch / land / market / twin / recs)
- `render_executive_sheet` — CEO 10s sheet + guided **Continue →** journey CTA
- Mounted on Hub, Market, Competition, Twin, AI Recs, Reports
- Tests: `tests/test_executive_sheet.py`

### Docs
- `docs/IMPLEMENTATION_SUMMARY_EXECUTIVE_SHEET.md`

## 2026-07-20 — Enterprise + demo 101% wave

### Added
- Hybrid/Live adapters with `AURA_LIVE_*_URL` (HTTP or `data/live_samples/*.json`)
- SQLite catalog mirror (`services/sqlite_store.py`, `AURA_DATA_BACKEND=sqlite`)
- Env-based auth passwords + optional salted SHA-256 hashes
- GitHub Actions CI + `.env.example`
- Demo wiring: Competition lens-only panels, Twin rival on canvas, Map what-if chart, Co-pilot intervene month

### Honest scope
- Demo control surface maximized; live KRERA requires partner URL credentials

## 2026-07-20 — P1 enterprise slice (RealEstateIQ plan)

### Added
- Land decision sheet (BUY/HOLD/PASS) on Competition → Land (`evaluate_land_decision`)
- Weekly marketing budget allocator from ROI quartiles
- Persisted Gradient Boosting artifact (`models/artifacts/`) — no retrain every click
- Native PDF board pack download on Executive Reports (`fpdf2`)
- Thin `repositories/catalog_repo.py` wrapping existing catalog/adapter
- Responsive CSS pass 320–1920 for tables / Folium height

### Dependencies
- `fpdf2`, `joblib` added to `requirements.txt`

### Docs
- `IMPLEMENTATION_SUMMARY.md` + `docs/IMPLEMENTATION_SUMMARY_P1.md`

## 2026-07-20 — P0 enterprise slice (RealEstateIQ plan)

### Added
- Design tokens + empty/error/loading/honesty UI primitives (`assets/design_tokens.css`, `components/states.py`)
- Data honesty banners on Executive Hub, Competition & Land, Map
- Executive Hub naming in module jump menu

### Fixed
- Logged-out deep links to `pages/*` now redirect to Executive Hub sign-in (no login collage under wrong page title)

### Preserved
- All existing modules, services, adapters, Co-pilot scoring, twin, reports
