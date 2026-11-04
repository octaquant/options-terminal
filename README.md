# OCTAQUANT Options Terminal

Free-first local Windows workspace for NIFTY and SENSEX options buyers.

## Run the main decision terminal
1. Install Python 3.10+ and enable Add Python to PATH.
2. Download this repository (Code -> Download ZIP) and extract it.
3. Double-click START_WINDOWS.bat.
4. The app opens locally, usually at http://localhost:8501.

## FYERS Non-trading API connector
Your FYERS Non-trading app is the correct app type for market-data access only. Official FYERS documentation says non-trading apps do not require static IP and grant profile, transaction info, historical data and quotes/market-data permissions; order placement is not granted. FYERS states its historical, quotes and real-time data are available to clients at zero datafeed fees. Brokerage, taxes and account charges are separate.

1. In FYERS API Dashboard, open your created Non-trading app (your screenshot showed it as Trading INSIGHT).
2. Keep the registered Redirect URL exactly:
   https://trade.fyers.in/api-login/redirect-uri/index.html
3. Copy App ID and App Secret from the app details. Never share them or commit them.
4. Download/extract this repo on your Windows PC.
5. Double-click START_FYERS_LIVE.bat.
6. In the local app sidebar, enter App ID and App Secret; click Generate FYERS login URL.
7. Click Open FYERS secure login, sign in and approve.
8. FYERS redirects to the registered redirect page. Copy only the value of the auth_code query parameter from the browser address bar and paste it into the local app. Do not share the auth code.
9. Click Exchange auth_code - Connect read-only.
10. Verify profile, then fetch NIFTY/SENSEX quotes and the option chain.

FYERS access tokens expire daily at 6:30 AM; authenticate again after expiry. This connector keeps the App Secret, auth code and access token in Streamlit session memory only; it does not write them to disk. It has no order placement, modification or cancellation calls.

## Connector scope / honest limitations
- Implemented: OAuth flow, profile verification, quote snapshots, option-chain snapshots and Greeks display where returned.
- Not yet implemented: persistent live WebSocket chart stream, automatic signal generation, broker order execution or fully tested live account integration.
- Index symbols are configured as NSE:NIFTY50-INDEX and BSE:SENSEX-INDEX. If FYERS rejects a symbol, verify the current symbol master and adjust it; do not interpret an error as a price.
- Do not treat checklist outputs as guaranteed or as investment advice.

## Security
- Never commit App ID + Secret together, access tokens, auth codes, PINs, TOTP seeds or broker session data.
- Never enter credentials into GitHub Pages or public web forms.
- Keep .gitignore in place. Local journal database is excluded.
- This software is a local decision-support tool; it does not place orders.

## GitHub Pages
index.html is a static landing page only. GitHub Pages cannot run Python/Streamlit.

## Dependencies
Python packages are open source. No paid hosting is required for local use. FYERS documents free API datafeed access for its clients; account charges, brokerage, statutory charges, rate limits and eligibility remain subject to FYERS terms.
