# Mentor Q&A — RealEstateIQ

**Audience:** mentors, industry collaborators, evaluators  
**Product:** RealEstateIQ (AURA-Market) — Developer Decision Support System  
**Micro-market:** Bagaluru / Aerospace Highway  

This document answers the questions mentors usually ask.  
For how the code is structured, see [`../02-architecture/ARCHITECTURE_OVERVIEW.md`](../02-architecture/ARCHITECTURE_OVERVIEW.md).

---

## Elevator answer (30 seconds)

> RealEstateIQ is an **executive decision support system** for real-estate developers.  
> It answers one question: **Should we launch / reprice this project at this ₹/sqft?**  
> Output is **GO / HOLD / NO-GO**, with evidence (market, competition, land, scenarios) and a **board pack** locked to that call.  
> It is **not** a chart museum, not live KRERA, and not a full SaaS platform yet.

---

## 1. What is this project about?

### Q1. What problem are you solving?

**A.** Developers about to launch do not get one clear answer from one system. They stitch Sales, Marketing, Finance, CRM, RERA PDFs, Excel, Power BI, and meetings. Reports conflict; competition “blind spots” get missed; leadership still cannot calmly answer: launch, wait, reprice, or buy land?

### Q2. What is the product in one line?

**A.** An **AI-assisted Developer Decision Support System** that locks one Hub launch call and walks supporting evidence into a board-ready pack for the Bagaluru corridor.

### Q3. What is it *not*?

**A.**

| Not this | Because |
|----------|---------|
| Live government RERA portal | Competition/land are curated seed unless live URLs are configured |
| City-wide digital twin | Scenario Engine = directional NumPy what-ifs |
| PropStack / full market database | Micro-market pilot, not city coverage |
| Native mobile app | Responsive Streamlit web |
| Multi-tenant enterprise SaaS | Capstone / pilot UI (auth is demo-grade) |

---

## 2. Why are we doing this?

### Q4. Why this project (mentor / industry ask)?

**A.** Mentor framing (SCOPE):

> Before I build, show me everything already built, being built, coming soon, and what land costs — so I can decide if my project will actually sell.

The project proves you can turn fragmented launch data into a **credible executive workflow** with honest data labelling.

### Q5. What success looks like (what we need to achieve)?

**A.**

1. One Hub **GO / HOLD / NO-GO** for project + ₹/sqft  
2. Evidence pages that **support** the Hub — they do not invent a second verdict  
3. Competition / land blind-spot visibility (approved, upcoming, UC, land)  
4. Scenario stress in **directional ₹ Cr**  
5. Reports **Section 0** matches Hub; assumptions / lineage labelled  
6. Demo usable by an unknown person in ~7 minutes  

**Out of scope for this phase:** live KRERA, SSO, RBAC, multi-tenancy, billing, K8s, SOC2.

---

## 3. What data were we given?

### Q6. What data does the app run on?

**A.** Runtime = **`data/*.csv` only** (no Excel at runtime).

| CSV (examples) | Role |
|----------------|------|
| `projects.csv` | Inventory, price, absorption |
| `rera_projects.csv` | Seed RERA approvals |
| `upcoming_projects.csv` | Advertised / coming soon |
| `under_construction.csv` | UC unsold pressure |
| `land_prices.csv` | Land ₹/sqft by micro-market |
| `zones.csv` | Map suitability inputs |
| `buyer_demographics.csv` | Booking-level buyer fields |
| `marketing_spends.csv` / `smc_spends.csv` | SMC spend signals |
| `monthly_absorption.csv` | Time series (SPC / forecast) |

### Q7. Where did the data come from?

**A.** Three honest buckets:

| Bucket | Source | Used how |
|--------|--------|----------|
| **Booking / spend workbooks** | Downloads Excels provided for the corridor | Ingested once into CSVs |
| **Curated seed** | Hand-built / scripted Bagaluru Aerospace Highway demo tables | Competition, land, zones, projects |
| **Not used** | `bengaluru_realestate_dataset.xlsx` | **Not loaded by the app** |

### Q8. Which Excel sheets (for the files we *did* use)?

**A.**

| File | Sheet |
|------|--------|
| Atmosphere / Blubelle / Ecopolitan demographic xlsx | **`SilverSky Launch Booking Data`** |
| SMC Spends Working File.xlsx | **`Sheet1`** (marketing long format), **`Sheet2`** (SMC share) |

### Q9. Where does the name “Bagaluru” appear?

**A.**

- **In the app:** seed CSVs / `build_seed_data.py` → e.g. `micro_market = Bagaluru / Aerospace Highway`  
- **In an unused Excel:** `bengaluru_realestate_dataset.xlsx` → sheet **`Areas_Data`** (area = Bagaluru) — **we do not use this file**  
- **In booking Excels:** City often says Bangalore / Bengaluru on sheet **`SilverSky Launch Booking Data`**

### Q10. Is the data “live”?

**A.** No by default. UI shows a **data contract**: measured (bookings/SMC) · seed (competition/land) · simulated (scenario ₹ Cr) · illustrative (map). Live adapters exist as stubs until `AURA_LIVE_*` is configured.

---

## 4. How should a mentor use the app?

### Q11. How do I log in and run a fair demo?

**A.**

1. Open https://aura-market-dss.streamlit.app  
2. Login: `admin` / `admin123`  
3. Sidebar: **IC Demo Mode ON**, **Visual Experience OFF** (optional later), **Board Mode ON** for presentation  
4. Path: **Hub → Market → Competition → Scenario Engine → Decision Explanation → Reports** (~7 min)  
5. Speak the data contract in the first 20 seconds  

### Q12. Where is the “only” recommendation?

**A.** **Executive Hub only** (GO / HOLD / NO-GO).  
Decision Explanation = **why**. Other modules = **evidence**. Reports reprint Hub Section 0.

### Q13. What is Scenario Engine vs “Digital Twin”?

**A.** Same underlying NumPy scenario math; UI name is **Scenario Engine** so we do not oversell a city twin. Figures are **directional / illustrative**.

### Q14. What is Visual Experience Mode?

**A.** Optional **presentation layer** (default OFF). Light 3D / motion only where it helps comparison, location, relationships, or scenarios. **Does not change** scoring, AI/ML, or navigation.

### Q15. What is the in-app Copilot?

**A.** A **page guide** (rules/templates). It explains metrics and next steps. It must **not** issue a second GO/HOLD.

---

## 5. Technical / academic questions

### Q16. What tech stack?

**A.** Python · Streamlit · pandas · Plotly · Folium · scikit-learn (GB forecast artifact) · fpdf2 (board pack) · pytest.

### Q17. Where does AI / ML sit?

**A.**

| Piece | Role |
|-------|------|
| Launch co-pilot / threat score | Rule + model composite for Hub verdict (existing engines) |
| Gradient Boosting | Project deep-dive forecast vs actual (lab) |
| Scenario Engine | Simulation (not generative LLM scoring) |
| Copilot | Guide only — not a new ML verdict |

Core scoring engines were treated as **frozen** during late UX polish.

### Q18. What architecture pattern?

**A.** Pages (UI) → components (chrome) → **services** (business logic) → adapters → CSV/data. Pages should not read CSVs directly. See architecture folder.

### Q19. What are known limitations?

**A.** Seed competition/land; demo auth; Streamlit multipage (not multi-tenant SaaS); map suitability is illustrative; scenario ₹ Cr not audited P&L. Documented in `docs/KNOWN_LIMITATIONS.md` and honesty banners in UI.

### Q20. How is this different from Power BI / Excel?

**A.** Power BI/Excel → many charts, no single locked call.  
RealEstateIQ → **one decision OS**: Hub verdict + guided evidence + board pack convergence.

---

## 6. Closing lines mentors can expect from students

**Product close:**  
> “One open decision — carried from Hub through evidence and scenario stress into a board pack — with measured vs seed vs simulated labelled.”

**Data close:**  
> “Buyer/SMC from corridor workbooks; competition and land are curated seed for Bagaluru Aerospace Highway — not live KRERA unless configured.”

**Scope close:**  
> “Capstone proves the decision workflow. Live feeds and enterprise security are Phase-2 productization.”

---

## Quick index of related repo docs

| Doc | Topic |
|-----|--------|
| `SCOPE.md` | Mentor ask + data mapping |
| `docs/WORKING_PROCESS.md` | Business process guide |
| `PRODUCT_EDGE.md` | Honest differentiators |
| `ENTERPRISE_REVIEW.md` | Scores + what is / isn’t enterprise-ready |
| `docs/DEMO_SCRIPT.md` | Older short demo notes (prefer mentor path above) |
