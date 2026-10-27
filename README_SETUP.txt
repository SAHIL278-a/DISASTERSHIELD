DISASTERSHIELD AI - WINDOWS SETUP

1. Install Python 3.11 or 3.12 (recommended for broad package compatibility).
2. Open Command Prompt in this project folder.
3. Create and activate a clean virtual environment:
   py -3.11 -m venv .venv
   .venv\Scripts\activate
4. Install packages:
   python -m pip install --upgrade pip
   pip install -r requirements.txt
5. Set your Google AI Studio API key in the current Command Prompt (do not share it):
   set GEMINI_API_KEY=YOUR_REAL_API_KEY
   Optional model override:
   set DISASTERSHIELD_AI_MODEL=gemma-4-26b-a4b-it
   Optional fallbacks (only model IDs enabled for your key):
   set DISASTERSHIELD_AI_FALLBACK_MODELS=gemma-4-31b-it
6. Start:
   python backend\app.py
7. Open:
   Dashboard: http://127.0.0.1:5000/
   Risk map:  http://127.0.0.1:5000/risk-map
   Health:    http://127.0.0.1:5000/health
   AI status: http://127.0.0.1:5000/api/ai/status

Gemma 4 primary model is gemma-4-26b-a4b-it. A second model is only tried if you configure
DISASTERSHIELD_AI_FALLBACK_MODELS. Model availability, billing/quota and access depend on
your Google AI Studio API key. The app cannot run hosted AI without a valid key and internet.

Safety: AI explanations are not official alerts. Verify warnings through NDMA SACHET and local
authorities. India emergency number: 112. Never use a demo risk score as an official forecast.

The virtual environment, Python caches and local database are intentionally not bundled into
the clean source ZIP. The database will be initialized by the application on first run.
