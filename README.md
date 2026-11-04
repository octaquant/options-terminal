# OCTAQUANT X-RAY Options Terminal

Free-first, local Windows, read-only decision-support terminal for NIFTY and SENSEX options buyers.

## Run
1. Install Python 3.12 x64.
2. Download this repository (Code -> Download ZIP) and extract it.
3. Double-click `START_FYERS_LIVE.bat`.
4. In the sidebar, enter the App ID and App Secret from your FYERS **Non-Trading** app.
5. Generate the secure login URL, authorize with FYERS, copy the `auth_code` from the redirect URL into the local app, and connect.
6. Use the four X-RAY tabs.

## X-RAY modules in this build
- **Market pulse:** NIFTY and SENSEX quote snapshots.
- **NIFTY 50 breadth:** editable FYERS symbol universe, quote batches, advancers/decliners, A/D ratio, leaders and laggards.
- **Visible liquidity:** FYERS depth snapshot, visible bid/ask quantities, imbalance and spread.
- **Options X-ray:** option-chain OI, change in OI, volume, LTP, IV and Greeks where returned by FYERS.
- **Setup validator:** user-confirmed checklist for S/R breakout, S/R rejection and trendline breakout; evidence score is a checklist ratio, not a win probability.
- **Risk calculator:** estimates lots within a ₹1,000 stop-risk budget using user-entered premium, stop and lot size.

## Data and interpretation limits
- This is an initial X-RAY integration, not yet a complete institutional footprint terminal.
- Quotes, depth and option chain are snapshots on button refresh. Persistent WebSocket streaming is not implemented in this build.
- The NIFTY 50 symbol list is an editable starting universe. Verify it against the latest official NSE constituents and FYERS symbol master before using it; membership and symbols can change.
- Visible depth is not hidden institutional liquidity. It can change or cancel before execution.
- Depth imbalance is not executed buy/sell delta. True footprint/CVD needs suitable trade-level bid/ask classification; this build does not claim to calculate it.
- Volume Profile, chart-based order blocks, absorption and liquidity sweeps are not yet implemented as validated live features.
- PCR is calculated over the returned option-chain strikes only. OI alone does not establish direction.
- Evidence score is not a statistical probability of winning. Backtesting and out-of-sample calibration are required before probability claims.
- Risk estimate excludes slippage, brokerage, taxes and charges; stop orders can slip and actual loss can exceed the estimate.
- No order placement, modification or cancellation functions are included.

## Security
- Never commit or share App Secret, auth_code, access token, PIN, TOTP seed or broker session data.
- Credentials and access token are held in local Streamlit session memory; do not publish screenshots containing secrets.
- This app is read-only. Do not treat a data/API error as a market price or signal.

## GitHub Pages
`index.html` is only a static landing page. GitHub Pages cannot run Python/Streamlit.

## Dependencies
Python packages are open source. No paid hosting is required for local execution. Brokerage, statutory charges and FYERS account/API eligibility remain subject to FYERS terms.
