# AURA-Market — Launch Decision Co-pilot

**Product (not a 12-page dashboard):** answer one real-world question —

> Can I launch / reprice at ₹X/sqft in Bagaluru this month?

**Verdict:** `GO` · `HOLD` · `NO-GO` with a proprietary **Launch Threat Score (0–100)** that fuses:

- Rival / upcoming price pressure  
- Under-construction unsold stock  
- Digital-twin blind-spot ₹ Cr loss + intervention recovery  
- Developer margin viability  
- SMC ROI tip + Map zone tip  

Depth modules (Competition, Map, Twin, Reports…) stay available under **Modules**.

## Live demo

https://aura-market-dss.streamlit.app  

Login: `admin` / `admin123`

After each push: Streamlit Cloud → **⋯ → Reboot app**.

## Why this is different

Indian mid-market teams have CRMs, Excel absorption, and ad hoc RERA checks.  
They do **not** have a single launch OS that converts competition blind spot → rupee exposure → three actions before brochure print.

## Local run

```bash
cd C:\Users\Admin\Projects\bagaluru-analytics-dss
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

## Repo

https://github.com/Tevskrishna/aura-market-dss
