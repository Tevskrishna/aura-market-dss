# Architecture

## Product type
**Decision Support System** (not a chart gallery) for Bagaluru micro-market developers.

## Layers

```
pages/          # Streamlit UI only (<300 lines each)
components/     # KPI cards, filters, layout/theme, auth chrome
services/       # Business logic (independently testable)
models/         # Dataclasses / contracts
utils/          # Plotly chart builders
config/         # Settings, schemas, demo auth
services/adapters.py  # Local CSV today → Live API tomorrow
data/           # Clean validated datasets
docs/           # Submission artefacts
tests/          # Service tests
```

## DMAIC mapping

| Phase | Modules |
|---|---|
| DEFINE | Home, DMAIC Workspace problem/CTQs |
| MEASURE | Market Overview, Buyer, Marketing, Competition |
| ANALYZE | Builder Deep Dive, DMAIC Pareto, Map feature importance |
| IMPROVE | Recommendations, Digital Twin, Forecasting, Map what-if |
| CONTROL | SPC, Executive Reports |

## Data adapters
`LocalCatalogAdapter` (default) loads validated CSVs.  
`LiveApiAdapter` raises until endpoints/credentials are configured (`DATA_ADAPTER_MODE=live`).

## Key shared contracts
- `FilterState` — Builder, Project, Date, Quarter  
- `DataCatalog` — single cleaned warehouse  
- `MarketBundle` / `MarketKPIs` — MEASURE scorecard  
- `CompetitionSnapshot` — mentor’s four layers  

Do **not** read CSVs inside pages.
