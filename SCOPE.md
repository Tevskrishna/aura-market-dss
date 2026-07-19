# Bagaluru Analytics DSS — Scope & Data Mapping

## Mentor ask (one line)

> Before I build, show me everything already built, being built, coming soon, and what land costs — so I can decide if my project will actually sell.

## Module map

| Mentor requirement | App module | Data source |
|---|---|---|
| RERA approved (last 3–5 yrs) | Competition Intelligence | `data/rera_projects.csv` (seed; replace with KRERA feed) |
| Advertised / upcoming | Competition Intelligence | `data/upcoming_projects.csv` |
| Ongoing / under construction | Competition Intelligence | `data/under_construction.csv` + sales inventory |
| Land prices by micro-market | Competition Intelligence + Map DSS | `data/land_prices.csv` |
| Short-term analytics / pricing | DMAIC pages 1–5 | `data/projects.csv`, `data/monthly_absorption.csv` |
| Suitability / livability / amenities | Map DSS | `data/zones.csv` + OSM-style amenity scores |
| Buyer demand profile | Buyer Demographics | Atmosphere / Blubelle / Ecopolitan booking Excels |
| Marketing efficiency signal | Buyer Demographics / Competition | SMC Spends workbook (Spend & % of budget) |

## Shared data files (Downloads)

| File | What it is | How we use it |
|---|---|---|
| Atmosphere demographic.xlsx | 780 confirmed bookings — unit mix, channel, pin, industry | Buyer persona for Atmosphere / North corridor demand |
| Blubelle demographic.xlsx | 305 bookings — strong investor channel | Investor vs end-user split |
| Ecopolitian demographic.xlsx | 1,497 bookings — Provident Ecopolitan | Bagaluru absorption buyer profile |
| SMC Spends Working File.xlsx | Quarterly SMC ₹ Cr + spend share by project | Marketing intensity vs competitive launches |
| Lead Data Insights Sample.pdf | Image/scan (no extractable text) | Needs OCR / manual legend later; not ingested |

## Phased delivery in this repo

1. **MVP (this build)** — full Streamlit shell: DMAIC + Map DSS + Competition blind-spot + demographics ingest from Excels.
2. **Next** — replace seed RERA/land rows with live KRERA / stamp-duty / listing scrapes; OCR the Lead PDF; add 1–3 year infrastructure shocks (metro / large adjoining launch).

## Success criteria (from mentor feedback)

- Developer can answer: “If I launch at price Y in Bagaluru next month, who else is already approved, advertising, or building?”
- Tool remains useful for **short-term** buyer/developer decisions; longer horizon flagged as future work (adjoining launches, metro uplift).
