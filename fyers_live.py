import streamlit as st
import pandas as pd
from fyers_apiv3 import fyersModel

REDIRECT_URI = "https://trade.fyers.in/api-login/redirect-uri/index.html"
INDEXES = {"NIFTY": "NSE:NIFTY50-INDEX", "SENSEX": "BSE:SENSEX-INDEX"}

st.set_page_config(page_title="OCTAQUANT · FYERS Data", page_icon="◈", layout="wide")
st.markdown("""
<style>
.stApp{background:#080d13;color:#e8eef4}.block-container{max-width:1250px;padding-top:2rem}
[data-testid="stMetric"]{background:#101923;border:1px solid #263545;padding:14px;border-radius:12px}
.stButton>button{background:#d8b36a;color:#10151b;border:0;font-weight:800}
</style>
""", unsafe_allow_html=True)
st.title("◈ OCTAQUANT · FYERS DATA CONNECTOR")
st.caption("NON-TRADING APP · MARKET DATA ONLY · NO ORDER FUNCTIONS")
st.info("Credentials and tokens stay in this local Streamlit session. Never paste App Secret, auth_code or access token into GitHub, chat, screenshots or public files.")

with st.sidebar:
    st.subheader("1 · FYERS App credentials")
    app_id = st.text_input("App ID")
    app_secret = st.text_input("App Secret", type="password")
    make_url = st.button("Generate FYERS login URL", use_container_width=True)

if make_url:
    if not app_id.strip() or not app_secret:
        st.error("Enter both App ID and App Secret.")
    else:
        try:
            session = fyersModel.SessionModel(client_id=app_id.strip(), secret_key=app_secret,
                redirect_uri=REDIRECT_URI, response_type="code", grant_type="authorization_code", state="OCTAQUANT")
            st.session_state["fyers_app_id"] = app_id.strip()
            st.session_state["fyers_app_secret"] = app_secret
            st.session_state["fyers_login_url"] = session.generate_authcode()
        except Exception as exc:
            st.error(f"Could not create login URL: {type(exc).__name__}: {exc}")

if st.session_state.get("fyers_login_url"):
    st.subheader("2 · Authorize your FYERS account")
    st.link_button("Open FYERS secure login", st.session_state["fyers_login_url"], use_container_width=True)
    st.markdown("After login, FYERS redirects to its registered redirect page. Copy only the value after auth_code= from the browser address bar. Do not share it.")
    with st.form("token_form"):
        auth_code = st.text_input("Paste auth_code here (local app only)", type="password")
        submit = st.form_submit_button("Exchange auth_code · Connect read-only")
    if submit:
        if not auth_code.strip():
            st.error("Paste the auth_code from the redirect URL.")
        else:
            try:
                session = fyersModel.SessionModel(client_id=st.session_state["fyers_app_id"],
                    secret_key=st.session_state["fyers_app_secret"], redirect_uri=REDIRECT_URI,
                    response_type="code", grant_type="authorization_code", state="OCTAQUANT")
                session.set_token(auth_code.strip())
                result = session.generate_token()
                token = (result or {}).get("access_token")
                if not token:
                    st.error("FYERS did not return an access token. Check App ID, Secret, redirect URL and auth_code; the code may have expired.")
                    st.json({k:v for k,v in (result or {}).items() if k not in ("access_token","refresh_token")})
                else:
                    st.session_state["fyers_access_token"] = token
                    st.session_state["fyers_api"] = fyersModel.FyersModel(
                        client_id=st.session_state["fyers_app_id"], token=token, is_async=False, log_path="")
                    st.success("FYERS session connected in this local app session.")
            except Exception as exc:
                st.error(f"Authentication failed: {type(exc).__name__}: {exc}")

api = st.session_state.get("fyers_api")
if api:
    st.success("CONNECTED · DATA ONLY")
    st.caption("FYERS access tokens expire daily at 6:30 AM. Re-authenticate when expired. No order functions are used.")
    if st.button("Verify profile"):
        try:
            profile = api.get_profile()
            if (profile or {}).get("s") == "ok":
                st.write("Profile verified:", (profile.get("data") or {}).get("name", "FYERS account"))
            else:
                st.error("Profile check failed.")
                st.json(profile)
        except Exception as exc:
            st.error(f"Profile request failed: {type(exc).__name__}: {exc}")

    st.subheader("3 · Index quotes")
    if st.button("Fetch NIFTY + SENSEX quotes", use_container_width=True):
        try:
            resp = api.quotes(data={"symbols": ",".join(INDEXES.values())})
            if (resp or {}).get("s") == "ok":
                rows = []
                for item in resp.get("d", []):
                    val = item.get("v", {})
                    rows.append({"Symbol": item.get("n", ""), "LTP": val.get("lp"),
                        "Change": val.get("ch"), "Change %": val.get("chp"),
                        "Open": val.get("open_price"), "High": val.get("high_price"),
                        "Low": val.get("low_price"), "Previous close": val.get("prev_close_price")})
                if rows:
                    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
                else:
                    st.warning("No quote rows returned. Verify index symbols against the current FYERS symbol master.")
            else:
                st.error("Quote request did not return success.")
                st.json(resp)
        except Exception as exc:
            st.error(f"Quote request failed: {type(exc).__name__}: {exc}")

    st.subheader("4 · Option chain + Greeks")
    index_name = st.selectbox("Underlying", list(INDEXES.keys()))
    strike_count = st.slider("Strikes on each side of ATM", 1, 20, 10)
    if st.button("Fetch option chain", use_container_width=True):
        try:
            resp = api.optionchain(data={"symbol": INDEXES[index_name], "strikecount": strike_count,
                "timestamp": "", "greeks": "1"})
            if (resp or {}).get("s") == "ok":
                data = resp.get("data", {})
                expiry_rows = data.get("expiryData", [])
                if expiry_rows:
                    st.caption("Available expiries: " + " · ".join(x.get("date", "") for x in expiry_rows))
                call_oi, put_oi = data.get("callOi", 0), data.get("putOi", 0)
                st.metric("PCR · returned strikes", round(put_oi / call_oi, 3) if call_oi else "—")
                chain = data.get("optionsChain", [])
                if chain:
                    frame = pd.DataFrame(chain)
                    frame = frame[frame.get("option_type", pd.Series(index=frame.index, dtype=str)).isin(["CE","PE"])].copy()
                    if "greeks" in frame.columns:
                        greeks = pd.json_normalize(frame["greeks"]).add_prefix("greeks_")
                        frame = pd.concat([frame.drop(columns=["greeks"]), greeks], axis=1)
                    cols = ["option_type","strike_price","ltp","ltpchp","bid","ask","oi","oich","volume",
                        "greeks_delta","greeks_gamma","greeks_theta","greeks_vega","greeks_iv"]
                    st.dataframe(frame[[c for c in cols if c in frame.columns]], use_container_width=True, hide_index=True)
                else:
                    st.warning("No option-chain rows returned.")
            else:
                st.error("Option-chain request did not return success.")
                st.json(resp)
        except Exception as exc:
            st.error(f"Option-chain request failed: {type(exc).__name__}: {exc}")

    if st.button("Disconnect local session"):
        for key in ["fyers_api","fyers_access_token","fyers_app_secret","fyers_app_id","fyers_login_url"]:
            st.session_state.pop(key, None)
        st.rerun()
else:
    st.warning("NOT CONNECTED · Complete the login steps above.")
    st.markdown("- OAuth login for your own Non-trading app\n- Profile verification\n- NIFTY and SENSEX quote snapshots\n- Option-chain snapshots with OI, IV and Greeks when returned\n- No order placement, modification or cancellation")
    st.caption("First integration build. Persistent WebSocket streaming and automatic signals are later steps. Verify symbol coverage and account permissions; an API error is never a market price.")
