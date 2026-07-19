# Known limitations (honest for company reviewers)

1. **Competition RERA / upcoming / land** use curated seed CSVs via `LocalCatalogAdapter`.  
   Live KRERA / registry APIs are stubbed (`LiveApiAdapter`) until credentials exist.

2. **Lead Data Insights PDF** is an image scan (0 extractable text).  
   `data/lead_insights.csv` is a curated funnel template grounded in booking channel mix.  
   Replace when OCR or Excel export is supplied.

3. **Sigma Level** uses documented DPMO = unsold/launched × 1e6.  
   With material unsold stock, sigma is mid/low — this is mathematically consistent with that formula.  
   Earlier pitch decks citing ~3.8–4.2σ imply a different opportunity base or healthier inventory snapshot.

4. **Digital Twin** uses a segmented Poisson engine (same buyer logic as SimPy design)  
   implemented in NumPy for reliability on Windows Python 3.14.

5. **Map suitability** is a Random Forest on engineered amenity/price features for 25 zones —  
   illustrative DSS, not a licensed GIS cadastral product.

6. **Forecasting** is short-horizon (trend + seasonality).  
   Mentor-requested 1–3 year metro / adjoining-launch shocks are **Phase-3**, not claimed here.

7. **Auth** is demo username/password only — replace with SSO before production SaaS deploy.

8. **Deploy** deferred by choice; run locally via Streamlit for submission walkthrough.
