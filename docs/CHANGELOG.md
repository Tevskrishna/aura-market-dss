# Changelog

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
