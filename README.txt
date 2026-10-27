DisasterShield AI — Risk Map integration patch

Install:
1. Stop Flask (Ctrl+C).
2. Back up frontend/map.html and frontend/map.js.
3. Copy this package's frontend/map.html and frontend/map.js into:
   C:\Users\Sahilraj\DISASTER_SHIELD_WINDOWS\frontend
4. Ensure Flask serves frontend static files at /static/<filename> and that /risk-map serves map.html. Your existing app.py previously included this route.
5. Run your existing Flask command and open http://127.0.0.1:5000/risk-map

Includes automatic geocoding for up to 5 recognized place mentions per refresh, manual Show location, category/location filters, dashboard navigation, and coloured display-only severity markers.

Important:
- Colours are inferred from alert wording; they are NOT official severity levels.
- Place mention is not a confirmed affected-area boundary.
- This patch does not add a real weather provider. Rainfall/flood scoring remains your existing prototype/manual-input risk engine until a real data source is configured.
- Internet is required for Leaflet tiles and public Nominatim geocoding.
- Keep existing app.py, ai_engine.py, risk_engine.py, database files, index.html, and GEMINI_API_KEY unchanged.
