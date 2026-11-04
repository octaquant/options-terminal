# Options Intelligence Terminal

A free-first local workspace for NIFTY and SENSEX options buyers.

## Run the original decision terminal
1. Install Python 3.10+ and enable **Add Python to PATH**.
2. Download this repository: **Code → Download ZIP**, then extract it.
3. Double-click `START_WINDOWS.bat`.
4. The app opens locally, usually at `http://localhost:8501`.

## Try the Angel One read-only connector
1. Create a SmartAPI app at [Angel One SmartAPI](https://smartapi.angelone.in/).
2. Download/extract this repository on your own Windows laptop.
3. Double-click `START_ANGELONE_LIVE.bat`.
4. Enter your API key, Client ID, trading PIN and TOTP setup secret only in the local app sidebar.
5. Press **Connect · Read-only**, then **Refresh NIFTY + SENSEX quotes**.

The connector currently attempts on-demand index LTP lookups. It is an integration prototype: the exact index symbol/token mapping may need adjustment based on Angel One's instrument master and API response. It does not yet provide an option chain, live streaming charts, automatic trade signals or order placement. Never treat a failed lookup as a price.

## GitHub Pages
The `index.html` file is only a static project landing page. Enable Pages in **Settings → Pages → Deploy from a branch → main → /(root)**. GitHub Pages cannot run Python/Streamlit.

## Security
- Do not commit API keys, PINs, TOTP secrets, JWTs, feed tokens or broker session data.
- Credentials typed in the local Streamlit session are not written to this repository or a local config file by this prototype.
- `.gitignore` excludes local databases and secret files.
- Do not enter broker credentials into the GitHub Pages website.
- The connector is read-only by design; no order endpoints are called.

## Dependencies and cost
Python packages are open-source and the project has no paid hosting requirement. Angel One SmartAPI access is subject to Angel One's current account, app, rate-limit and market-data terms. Verify current eligibility and charges with Angel One; this repository does not guarantee that every API feature is free.

## Scope / limitations
- Original app: TradingView chart embed, manual regime and setup checklists, manual-input Black–Scholes Greek estimates, local SQLite journal and two-trade guard.
- Angel One connector: login attempt and on-demand index LTP lookup prototype only.
- No verified live option-chain feed is connected yet.
- No guaranteed accuracy, trade outcome or profit. This is a decision-support tool, not investment advice.
