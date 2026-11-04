# Options Intelligence Terminal

A free-first local Streamlit workspace for NIFTY and SENSEX options buyers.

## Current files
- `app.py`: dashboard, manual setup checklist, Black–Scholes estimate calculator and local trade journal.
- `requirements.txt`: Python dependencies.
- `START_WINDOWS.bat`: Windows launcher.
- `index.html`: static GitHub Pages project page (not the Python terminal).

## Run the actual terminal on Windows
1. Install Python 3.10+ and enable "Add Python to PATH".
2. Download this repository (Code → Download ZIP) and extract it.
3. Double-click `START_WINDOWS.bat`.
4. The Streamlit app opens locally, usually at `http://localhost:8501`.

## GitHub Pages
Enable Pages in Settings → Pages → Deploy from a branch → `main` → `/ (root)`.
The static page will be served at `https://octaquant.github.io/options-terminal/` after deployment finishes.
GitHub Pages cannot run Python/Streamlit; it only hosts the static landing page.

## Data and security status
- Live broker market data is NOT connected.
- TradingView embeds may display chart data subject to TradingView/exchange access and delay rules.
- NSE public reports are not a guaranteed real-time API.
- Do not put Angel One API keys, API secret, TOTP seed, PIN, password or access token in this public repository.
- No automatic order placement is implemented.

## Important
This application is a decision-support/journaling tool, not a buy/sell guarantee. Validate expiry, lot size, premium, liquidity, spread, charges and risk independently. Greeks use a simplified Black–Scholes model and are estimates.
