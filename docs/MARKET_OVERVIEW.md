# Market Overview Module

## Why it exists
Foundation MEASURE layer of the Decision Intelligence Platform. Every later
module reuses its catalog, filters, and KPI contracts.

## Business problem
Developers lack a single filtered view of projects, bookings, marketing spend,
sales value, absorption, and buyer mix before launch / intervention decisions.

## DMAIC
- **DEFINE** — CTQ scorecard fields on `MarketKPIs`
- **MEASURE** — cleaned frames only; validation gates the page

## Expected output
Global filters → KPI cards → Plotly charts → CSV download

## Dependencies
`config`, `services.data_loader`, `services.filter_service`, `services.market_service`,
`components.*`, `utils.charts`

## Future extensions
Live feeds, peer benchmarks, workspace-saved filters
