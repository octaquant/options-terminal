import streamlit as st
import pandas as pd
from fyers_apiv3 import fyersModel
from xray_engine import NIFTY50_SYMBOLS, quote_rows, breadth_metrics, depth_metrics, option_chain_metrics, confluence_score

REDIRECT_URI = "https://trade.fyers.in/api-login/redirect-uri/index.html"
INDEXES = {"NIFTY": "NSE:NIFTY50-INDEX", "SENSEX": "BSE:SENSEX-INDEX"}

st.set_page_config(page_title="OCTAQUANT X-RAY", page_icon="◈", layout="wide")
st.markdown("""
<style>
.stApp{background:#080d13;color:#e8eef4}.block-container{max-width:1800px;padding-top:1.1rem}
[data-testid="stMetric"]{background:#101923;border:1px solid #263545;padding:12px;border-radius:10px}
.stButton>button{background:#d8b36a;color:#10151b;border:0;font-weight:800}
[data-testid="stTabs"] button{font-weight:700}
div[data-testid="stDataFrame"]{border:1px solid #263545;border-radius:8px}
</style>
""", unsafe_allow_html=True)
st.title("◈ OCTAQUANT · MARKET X-RAY")
st.caption("PRICE ACTION  /  MARKET BREADTH  /  VISIBLE LIQUIDITY  /  OPTIONS INTELLIGENCE  /  TRADE VALIDATION")
st.info("Read-only terminal. No order placement. Snapshot data is not a tick-by-tick feed. Never share App Secret, auth_code or access token.")

with st.sidebar:
    st.header("FYERS · DATA LINK")
    app_id=st.text_input("App ID",value=st.session_state.get("fyers_app_id",""))
    app_secret=st.text_input("App Secret",type="password")
    if st.button("Generate secure login URL",use_container_width=True):
        if app_id.strip() and app_secret:
            try:
                sess=fyersModel.SessionModel(client_id=app_id.strip(),secret_key=app_secret,redirect_uri=REDIRECT_URI,response_type="code",grant_type="authorization_code",state="OCTAQUANT")
                st.session_state["fyers_app_id"]=app_id.strip()
                st.session_state["fyers_app_secret"]=app_secret
                st.session_state["fyers_login_url"]=sess.generate_authcode()
            except Exception as e: st.error(f"{type(e).__name__}: {e}")
        else: st.error("App ID and App Secret required.")
    if st.session_state.get("fyers_login_url"):
        st.link_button("Open FYERS login",st.session_state["fyers_login_url"],use_container_width=True)
        st.caption("After approval, copy auth_code from redirect URL into the field below.")
        code=st.text_input("auth_code (local only)",type="password")
        if st.button("Connect read-only",use_container_width=True):
            try:
                sess=fyersModel.SessionModel(client_id=st.session_state["fyers_app_id"],secret_key=st.session_state["fyers_app_secret"],redirect_uri=REDIRECT_URI,response_type="code",grant_type="authorization_code",state="OCTAQUANT")
                sess.set_token(code.strip()); result=sess.generate_token()
                token=(result or {}).get("access_token")
                if not token: st.error("No access token returned. Check credentials and auth_code expiry.")
                else:
                    st.session_state["fyers_access_token"]=token
                    st.session_state["fyers_api"]=fyersModel.FyersModel(client_id=st.session_state["fyers_app_id"],token=token,is_async=False,log_path="")
                    st.success("Connected.")
            except Exception as e: st.error(f"Authentication failed: {type(e).__name__}: {e}")
    if st.session_state.get("fyers_api"):
        st.success("CONNECTED · DATA ONLY")
        st.caption("Token/session expiry may require fresh login.")
        if st.button("Disconnect"):
            for k in ["fyers_api","fyers_access_token","fyers_app_secret","fyers_login_url"]: st.session_state.pop(k,None)
            st.rerun()
    st.divider()
    st.caption("Risk discipline")
    st.metric("Max risk / trade","₹1,000")
    st.metric("Max trades / day","2")

api=st.session_state.get("fyers_api")
if not api:
    st.warning("Connect your FYERS Non-Trading app from the sidebar to load market data.")
    st.markdown("### What this build contains")
    st.markdown("- NIFTY 50 advance/decline breadth snapshot\n- Visible bid/ask depth imbalance and spread\n- Option-chain OI, volume and Greeks view\n- Setup validation checklist and risk calculator")
    st.stop()

# Top-level market snapshot
st.subheader("MARKET PULSE")
if st.button("Refresh NIFTY + SENSEX snapshots",type="primary"):
    try:
        resp=api.quotes(data={"symbols":",".join(INDEXES.values())})
        if (resp or {}).get("s")=="ok":
            q=quote_rows(resp)
            st.session_state["index_quotes"]=q
        else: st.error(f"Quote API: {resp}")
    except Exception as e: st.error(f"Quote request: {type(e).__name__}: {e}")
q=st.session_state.get("index_quotes",pd.DataFrame())
if not q.empty:
    cols=st.columns(len(q))
    for col,(_,row) in zip(cols,q.iterrows()):
        with col:
            st.metric(str(row["Symbol"]),f"{row['LTP']}",f"{row['Change']} ({row['Change %']}%)")
    st.caption("Snapshot values: last successful refresh; not guaranteed streaming/live tick data.")
else: st.caption("No index snapshot yet. Click Refresh.")

tabs=st.tabs(["01 · BREADTH","02 · LIQUIDITY","03 · OPTIONS X-RAY","04 · SETUP VALIDATOR"])
with tabs[0]:
    st.subheader("NIFTY 50 · ADVANCE / DECLINE")
    st.caption("Editable symbol universe. Verify it against the latest NSE NIFTY 50 constituents before relying on breadth; constituents can change.")
    default="\n".join(NIFTY50_SYMBOLS)
    symbols_text=st.text_area("FYERS equity symbols · one per line",value=st.session_state.get("breadth_symbols",default),height=150)
    st.session_state["breadth_symbols"]=symbols_text
    symbols=[s.strip().upper() for s in symbols_text.splitlines() if s.strip()]
    if st.button("Scan constituent breadth",key="breadth_scan"):
        try:
            frames=[]
            for start in range(0,len(symbols),50):
                rr=api.quotes(data={"symbols":",".join(symbols[start:start+50])})
                if (rr or {}).get("s")=="ok": frames.append(quote_rows(rr))
                else: st.warning(f"Quote batch {start//50+1} failed: {rr}")
            if frames: st.session_state["breadth_frame"]=pd.concat(frames,ignore_index=True)
            else: st.error("No constituent quotes returned.")
        except Exception as e: st.error(f"Breadth scan failed: {type(e).__name__}: {e}")
    bf=st.session_state.get("breadth_frame",pd.DataFrame())
    if not bf.empty:
        b=breadth_metrics(bf)
        a=st.columns(4)
        a[0].metric("Advancers",b["advancers"]); a[1].metric("Decliners",b["decliners"])
        a[2].metric("Unchanged",b["unchanged"]); a[3].metric("A/D ratio",b["ad_ratio"] if b["ad_ratio"] is not None else "—")
        st.metric("Net breadth",f"{b['net']:+d}",f"{b['breadth_pct']}% of scanned stocks")
        left,right=st.columns(2)
        with left: st.markdown("**Top positive movers**"); st.dataframe(b["leaders"],use_container_width=True,hide_index=True)
        with right: st.markdown("**Top negative movers**"); st.dataframe(b["laggards"],use_container_width=True,hide_index=True)
        st.dataframe(bf.sort_values("Change %",ascending=False),use_container_width=True,hide_index=True)
    else: st.info("Breadth data will appear after a scan. Failed symbols are not silently counted.")

with tabs[1]:
    st.subheader("VISIBLE ORDER-BOOK LIQUIDITY")
    st.caption("FYERS depth endpoint snapshot. This is displayed visible depth, not hidden institutional orders or executed footprint volume.")
    dcol1,dcol2=st.columns([2,1])
    with dcol1: depth_symbol=st.text_input("FYERS symbol",value="NSE:NIFTY50-INDEX")
    with dcol2: depth_flag=st.selectbox("Depth response mode",["1","0"],index=0,help="FYERS depth API ohlcv_flag parameter.")
    if st.button("Fetch market depth",key="depth_fetch"):
        try:
            dr=api.depth(data={"symbol":depth_symbol.strip(),"ohlcv_flag":depth_flag})
            if (dr or {}).get("s")=="ok": st.session_state["depth_response"]=dr
            else: st.error(f"Depth API response: {dr}")
        except Exception as e: st.error(f"Depth request failed: {type(e).__name__}: {e}")
    dr=st.session_state.get("depth_response")
    if dr:
        dm=depth_metrics(dr)
        c=st.columns(4)
        c[0].metric("Visible bid qty",f"{dm['bid_qty']:,.0f}")
        c[1].metric("Visible ask qty",f"{dm['ask_qty']:,.0f}")
        c[2].metric("Bid/ask imbalance",f"{dm['imbalance']}%" if dm["imbalance"] is not None else "—")
        c[3].metric("Best-level spread",dm["spread"] if dm["spread"] is not None else "—")
        l,r=st.columns(2)
        with l:
            st.markdown("**Bid ladder**")
            st.dataframe(pd.DataFrame(dm["bids"],columns=["Visible quantity","Price"]),use_container_width=True,hide_index=True)
        with r:
            st.markdown("**Ask ladder**")
            st.dataframe(pd.DataFrame(dm["asks"],columns=["Visible quantity","Price"]),use_container_width=True,hide_index=True)
        with st.expander("Raw depth response"): st.json(dr)
    else: st.info("Fetch depth to inspect visible bid/ask liquidity.")

with tabs[2]:
    st.subheader("OPTIONS CHAIN · OI / VOLUME / IV / GREEKS")
    under=st.selectbox("Underlying",list(INDEXES.keys()),key="chain_under")
    strikes=st.slider("Strikes around ATM",1,20,10,key="chain_strikes")
    if st.button("Fetch option-chain X-ray",key="chain_fetch"):
        try:
            cr=api.optionchain(data={"symbol":INDEXES[under],"strikecount":strikes,"timestamp":"","greeks":"1"})
            if (cr or {}).get("s")=="ok":
                cd=cr.get("data",{})
                st.session_state["chain_response"]=cr
                st.session_state["chain_rows"]=pd.DataFrame(cd.get("optionsChain",[]))
                st.session_state["chain_meta"]={"callOi":cd.get("callOi",0),"putOi":cd.get("putOi",0),"expiryData":cd.get("expiryData",[])}
            else: st.error(f"Option chain response: {cr}")
        except Exception as e: st.error(f"Option-chain request failed: {type(e).__name__}: {e}")
    chain=st.session_state.get("chain_rows",pd.DataFrame())
    if not chain.empty:
        cm=option_chain_metrics(chain)
        meta=st.session_state.get("chain_meta",{})
        c=st.columns(4)
        c[0].metric("PCR · returned strikes",cm.get("pcr","—"))
        c[1].metric("Call OI",f"{cm.get('call_oi',0):,.0f}")
        c[2].metric("Put OI",f"{cm.get('put_oi',0):,.0f}")
        c[3].metric("Expiry choices",len(meta.get("expiryData",[])))
        view=chain.copy()
        if "greeks" in view:
            g=pd.json_normalize(view["greeks"]).add_prefix("G_")
            view=pd.concat([view.drop(columns=["greeks"]),g],axis=1)
        preferred=["option_type","strike_price","ltp","ltpchp","bid","ask","oi","oich","volume","G_delta","G_gamma","G_theta","G_vega","G_iv"]
        st.dataframe(view[[x for x in preferred if x in view.columns]],use_container_width=True,hide_index=True)
        st.caption("PCR and OI are limited to returned strikes. OI alone does not prove bullish/bearish positioning; interpret change in OI with price, volume and IV.")
    else: st.info("Fetch option chain to populate strike-level analysis.")

with tabs[3]:
    st.subheader("TRADE SETUP VALIDATOR")
    st.caption("Use this as a disciplined evidence checklist, not a predictive probability. Select only evidence you have actually verified.")
    direction=st.radio("Trade direction",["CE / Bullish","PE / Bearish"],horizontal=True)
    setup=st.selectbox("Your setup",["Support / resistance breakout","Support / resistance rejection","Trendline breakout"])
    st.markdown("**Tick only when confirmed on your chart/data**")
    checks={}
    labels=[
        ("structure","Price structure confirms the chosen setup"),
        ("close","Candle close confirms; not just a wick"),
        ("volume","Volume supports the move"),
        ("vwap","VWAP / intraday trend agrees"),
        ("liquidity","Visible liquidity behaviour does not contradict entry"),
        ("chain","Option-chain behaviour supports direction"),
        ("premium","Option spread and premium movement are tradable"),
        ("rr","Reward-to-risk is at least 1.5:1"),
    ]
    grid=st.columns(2)
    for i,(key,label) in enumerate(labels):
        with grid[i%2]: checks[key]=st.checkbox(label,key="check_"+key)
    score=confluence_score(checks)
    st.metric("Evidence score",f"{score}/100" if score is not None else "—")
    if score is not None:
        if score>=75: st.success("Checklist confluence is strong. Still wait for your trigger and verify stop distance.")
        elif score>=50: st.warning("Mixed evidence. Wait for missing confirmations; avoid forcing an entry.")
        else: st.error("Weak evidence. NO TRADE is the disciplined default.")
    st.divider()
    st.markdown("**Position sizing · ₹1,000 hard risk cap**")
    x,y,z=st.columns(3)
    with x: entry=st.number_input("Option entry premium",min_value=0.05,value=100.0,step=0.05)
    with y: stop=st.number_input("Option stop premium",min_value=0.0,value=80.0,step=0.05)
    with z: lot=st.number_input("Lot size",min_value=1,value=65,step=1)
    per_unit=max(entry-stop,0)
    risk_per_lot=per_unit*lot
    lots=int(1000//risk_per_lot) if risk_per_lot>0 else 0
    st.metric("Estimated risk per lot",f"₹{risk_per_lot:,.2f}")
    st.metric("Max lots within ₹1,000",lots)
    if lots==0: st.error("No valid lot fits the risk cap at this stop distance.")
    else: st.info(f"Estimated total stop risk: ₹{lots*risk_per_lot:,.2f} before slippage, brokerage and charges.")
    st.caption("Lot size is user-entered and must match the current contract specification. Stops can slip; actual loss may exceed estimate.")

st.divider()
st.caption("OCTAQUANT X-RAY v0.2 · Snapshot analytics · Read-only · No order placement · Not investment advice")
