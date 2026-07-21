# AURA-Market — Launch Decision Co-pilot

**Product:** RealEstateIQ — AI-powered **Developer Decision Support System** for Bagaluru launch / land calls.  
Not a chart museum. One guided decision journey.

> **Should we launch / reprice at ₹X/sqft this month?** → `GO` · `HOLD` · `NO-GO`

Honest edge (what is rare vs what we do **not** claim): [`PRODUCT_EDGE.md`](PRODUCT_EDGE.md)

## Problem we solve

Developers stitch Sales, Marketing, Finance, CRM, RERA PDFs, Excel, and meetings. Reports conflict.  
RealEstateIQ gives **one Hub recommendation**; every other module is **evidence**.

Narrative: [`docs/WORKING_PROCESS.md`](docs/WORKING_PROCESS.md) · Flow: [`DECISION_FLOW.md`](DECISION_FLOW.md)

**Mentors:** start at [`mentor/README.md`](mentor/README.md) — Q&A + architecture packs (two folders).


## Share on phone (mobile)

1. Open **https://aura-market-dss.streamlit.app** in Chrome / Safari on your phone.  
2. Login: `admin` / `admin123` (or `demo` / `demo123`).  
3. Tap **☰** (top-left orange) for Workspaces, Copilot, tour replay.  
4. On Hub: set project + ₹/sqft → read GO/HOLD/NO-GO.  
5. Use **Continue →** — layout stacks for narrow screens; journey pipeline scrolls sideways.  
6. Sticky footer shows current module; live strip shows open decision freshness.

After every GitHub push: Streamlit Cloud → **⋯ → Reboot app** so the phone sees the latest UI.

## Working process

```
Hub → Market → Competition → Buyer → Marketing → DMAIC → Project
  → Twin → Decision Explanation → SPC → Reports
```

## Local run

```bash
cd C:\Users\Admin\Projects\bagaluru-analytics-dss
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

On the same Wi‑Fi, phone can open `http://<your-PC-LAN-IP>:8501` while Streamlit is running.

## Repo

https://github.com/Tevskrishna/aura-market-dss
