import streamlit as st
import pyotp
from SmartApi import SmartConnect
from datetime import datetime

st.set_page_config(page_title="Angel One · Live Data", page_icon="◈", layout="wide")
st.markdown("""
<style>
.stApp{background:#080d13;color:#e8eef4}.block-container{max-width:1100px;padding-top:2rem}
h1,h2,h3{letter-spacing:-.03em}.stButton>button{background:#d8b36a;color:#10151b;border:0;font-weight:800}
[data-testid="stMetric"]{background:#101923;border:1px solid #243241;padding:18px;border-radius:12px}
</style>
""",unsafe_allow_html=True)
st.title("◈ OPTIONS INTELLIGENCE")
st.caption("ANGEL ONE SMARTAPI · READ-ONLY MARKET DATA CONNECTOR")
st.warning("Credentials are entered only into this local app session. Never paste them into GitHub or chat. This prototype does not place orders.")

with st.sidebar:
    st.subheader("Angel One connection")
    api_key=st.text_input("SmartAPI Key",type="password")
    client=st.text_input("Angel One Client ID")
    pin=st.text_input("Trading PIN",type="password")
    totp_seed=st.text_input("TOTP secret (QR key)",type="password",help="Enter the authenticator setup key, not the 6-digit changing OTP.")
    connect=st.button("Connect · Read-only",use_container_width=True)
    st.caption("Connection is not saved. Re-enter after app restart/session expiry.")

if connect:
    if not all([api_key,client,pin,totp_seed]):
        st.error("Fill all four fields.")
    else:
        try:
            otp=pyotp.TOTP(totp_seed.replace(" ","")).now()
            api=SmartConnect(api_key=api_key)
            response=api.generateSession(client,pin,otp)
            if response and response.get("status"):
                st.session_state["angel_api"]=api
                st.session_state["angel_client"]=client
                st.session_state["angel_connected"]=True
                st.success("Angel One session connected.")
            else:
                st.session_state["angel_connected"]=False
                st.error("Login rejected by Angel One. Check API key, Client ID, PIN, TOTP and SmartAPI app permissions.")
                st.code(str(response)[:1200])
        except Exception as exc:
            st.session_state["angel_connected"]=False
            st.error(f"Connection failed: {type(exc).__name__}: {exc}")

if st.session_state.get("angel_connected"):
    st.success("CONNECTED · Read-only session")
    api=st.session_state["angel_api"]
    st.caption("Quotes are requested on demand. No automatic order placement is present.")
    if st.button("Refresh NIFTY + SENSEX quotes"):
        results=[]
        for exch,query,label in [("NSE","Nifty 50","NIFTY"),("BSE","SENSEX","SENSEX")]:
            try:
                found=api.searchScrip(exch,query)
                rows=(found or {}).get("data") or []
                if not rows:
                    results.append({"Index":label,"Status":"Scrip not found","LTP":"—"})
                    continue
                item=rows[0]
                quote=api.ltpData(exch,item.get("tradingsymbol"),item.get("symboltoken"))
                q=(quote or {}).get("data") or {}
                results.append({"Index":label,"Status":"OK" if quote.get("status") else "Quote error","LTP":q.get("ltp","—"),"Symbol":item.get("tradingsymbol"),"Token":item.get("symboltoken")})
            except Exception as exc:
                results.append({"Index":label,"Status":f"{type(exc).__name__}: {exc}","LTP":"—"})
        st.session_state["quotes"]=results
    if "quotes" in st.session_state:
        st.dataframe(st.session_state["quotes"],use_container_width=True,hide_index=True)
    st.caption("If an index symbol search fails, we will correct the exchange symbol/token using Angel One's instrument master. Do not infer a live price from a failed response.")
    if st.button("Disconnect"):
        try: api.terminateSession(st.session_state["angel_client"])
        except Exception: pass
        for key in ["angel_api","angel_client","angel_connected","quotes"]:
            st.session_state.pop(key,None)
        st.rerun()
else:
    st.info("NOT CONNECTED · Enter your own SmartAPI credentials in the sidebar after creating an Angel One SmartAPI app.")
    st.markdown("### What this connector does")
    st.markdown("- Attempts authenticated, on-demand index LTP requests for NIFTY and SENSEX.\n- Displays connection failures honestly.\n- Does not submit, modify or cancel orders.\n- Does not write credentials to files or GitHub.")
    st.markdown("### Start here")
    st.markdown("[Angel One SmartAPI portal](https://smartapi.angelone.in/) · [Official documentation](https://smartapi.angelone.in/docs)")
