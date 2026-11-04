OPTIONS INTELLIGENCE TERMINAL — FREE LOCAL MVP

WHAT THIS BUILD DOES
- Professional dark terminal interface for NIFTY and SENSEX.
- TradingView chart embed (internet required; quote availability depends on TradingView/exchange entitlements).
- Manual market-regime checklist.
- Your two setup confirmation checklists: Support/Resistance and Trendline Breakout.
- Black-Scholes Greek estimate calculator (manual inputs).
- Local SQLite trade journal and a two-trades-per-day limit.
- Blocks planned trades with more than Rs 1,000 gross premium risk.

IMPORTANT DATA LIMITATION
This MVP does NOT fetch official live NSE option-chain/Greeks data. It does not fake live prices. Live option-chain integration requires an authorized data feed. Some broker APIs charge for market data. The UI and local calculations are free.

REQUIREMENTS
- Windows 10/11
- Python 3.10 or newer
- Internet for package install and TradingView chart embed

START
1. Install Python from https://www.python.org/downloads/ (enable Add Python to PATH).
2. Extract this folder.
3. Double-click START_WINDOWS.bat.
4. Browser opens the local terminal, usually at http://localhost:8501.

DATA PRIVACY
Trade journal is stored locally in terminal.db in this folder. Do not share broker passwords, PINs, TOTP secrets or access tokens in chat. A future broker connector should use local environment variables and read-only permissions wherever possible.

NOT FINANCIAL ADVICE
No automatic order placement. Greeks are approximations. Verify prices, lot sizes, charges, expiry and risk before trading.
