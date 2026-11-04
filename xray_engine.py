"""OCTAQUANT X-RAY analytics. Snapshot analytics only; no broker order functions."""
from __future__ import annotations
import math
import pandas as pd

NIFTY50_SYMBOLS = [
"NSE:ADANIENT-EQ","NSE:ADANIPORTS-EQ","NSE:APOLLOHOSP-EQ","NSE:ASIANPAINT-EQ",
"NSE:AXISBANK-EQ","NSE:BAJAJ-AUTO-EQ","NSE:BAJFINANCE-EQ","NSE:BAJAJFINSV-EQ",
"NSE:BEL-EQ","NSE:BHARTIARTL-EQ","NSE:CIPLA-EQ","NSE:COALINDIA-EQ",
"NSE:DRREDDY-EQ","NSE:EICHERMOT-EQ","NSE:ETERNAL-EQ","NSE:GRASIM-EQ",
"NSE:HCLTECH-EQ","NSE:HDFCBANK-EQ","NSE:HDFCLIFE-EQ","NSE:HEROMOTOCO-EQ",
"NSE:HINDALCO-EQ","NSE:HINDUNILVR-EQ","NSE:ICICIBANK-EQ","NSE:INDUSINDBK-EQ",
"NSE:INFY-EQ","NSE:ITC-EQ","NSE:JIOFIN-EQ","NSE:JSWSTEEL-EQ",
"NSE:KOTAKBANK-EQ","NSE:LT-EQ","NSE:M&M-EQ","NSE:MARUTI-EQ",
"NSE:NESTLEIND-EQ","NSE:NTPC-EQ","NSE:ONGC-EQ","NSE:POWERGRID-EQ",
"NSE:RELIANCE-EQ","NSE:SBILIFE-EQ","NSE:SBIN-EQ","NSE:SHRIRAMFIN-EQ",
"NSE:SUNPHARMA-EQ","NSE:TATACONSUM-EQ","NSE:TATAMOTORS-EQ","NSE:TATASTEEL-EQ",
"NSE:TCS-EQ","NSE:TECHM-EQ","NSE:TITAN-EQ","NSE:ULTRACEMCO-EQ",
"NSE:WIPRO-EQ","NSE:MAXHEALTH-EQ"
]

def quote_rows(resp):
    rows=[]
    for item in (resp or {}).get("d", []):
        v=item.get("v", {}) or {}
        rows.append({"Symbol":item.get("n",""),"LTP":v.get("lp"),"Change":v.get("ch"),
                     "Change %":v.get("chp"),"Volume":v.get("volume"),
                     "Open":v.get("open_price"),"High":v.get("high_price"),
                     "Low":v.get("low_price"),"Prev Close":v.get("prev_close_price")})
    return pd.DataFrame(rows)

def breadth_metrics(frame):
    if frame is None or frame.empty or "Change %" not in frame:
        return {"advancers":0,"decliners":0,"unchanged":0,"total":0,"ad_ratio":None,
                "breadth_pct":None,"net":0,"leaders":pd.DataFrame(),"laggards":pd.DataFrame()}
    x=frame.copy()
    x["Change %"]=pd.to_numeric(x["Change %"],errors="coerce")
    x=x.dropna(subset=["Change %"])
    adv=int((x["Change %"]>0).sum()); dec=int((x["Change %"]<0).sum())
    unc=int((x["Change %"]==0).sum()); total=len(x)
    return {"advancers":adv,"decliners":dec,"unchanged":unc,"total":total,
            "ad_ratio":round(adv/dec,2) if dec else (float("inf") if adv else None),
            "breadth_pct":round((adv-dec)/total*100,1) if total else None,"net":adv-dec,
            "leaders":x.nlargest(5,"Change %")[["Symbol","Change %"]],
            "laggards":x.nsmallest(5,"Change %")[["Symbol","Change %"]]}

def depth_metrics(resp):
    """Summarise visible top-five depth. This is not hidden/institutional liquidity."""
    root=(resp or {}).get("d",{}) or {}
    if isinstance(root,list): root=root[0] if root else {}
    book=root.get(" oms",None) or root.get("depth",None) or root
    bids=book.get("bids",[]) or book.get("buy",[]) or []
    asks=book.get("asks",[]) or book.get("sell",[]) or []
    def norm(level):
        if isinstance(level,dict):
            return float(level.get("volume",level.get("qty",level.get("quantity",0))) or 0), level.get("price",level.get("rate"))
        if isinstance(level,(list,tuple)) and len(level)>=2:
            return float(level[1] or 0),level[0]
        return 0,None
    b=[norm(z) for z in bids]; a=[norm(z) for z in asks]
    bv=sum(z[0] for z in b); av=sum(z[0] for z in a)
    total=bv+av
    bp=next((float(z[1]) for z in b if z[1] is not None),None)
    ap=next((float(z[1]) for z in a if z[1] is not None),None)
    return {"bid_qty":bv,"ask_qty":av,"imbalance":round((bv-av)/total*100,1) if total else None,
            "spread":round(ap-bp,2) if ap is not None and bp is not None else None,
            "bids":b,"asks":a,"raw":root}

def option_chain_metrics(chain):
    if chain is None or len(chain)==0: return {}
    x=chain.copy()
    for c in ["oi","oich","volume","ltp","strike_price","ltpchp"]:
        if c in x: x[c]=pd.to_numeric(x[c],errors="coerce")
    ce=x[x.get("option_type",pd.Series(index=x.index,dtype=str))=="CE"]
    pe=x[x.get("option_type",pd.Series(index=x.index,dtype=str))=="PE"]
    coi=float(ce["oi"].fillna(0).sum()) if "oi" in ce else 0
    poi=float(pe["oi"].fillna(0).sum()) if "oi" in pe else 0
    return {"pcr":round(poi/coi,3) if coi else None,"call_oi":coi,"put_oi":poi,
            "ce":ce,"pe":pe,"chain":x}

def confluence_score(checks):
    """Transparent checklist score, not a probability or forecast."""
    valid=[v for v in checks.values() if v in (True,False)]
    if not valid: return None
    return round(sum(valid)/len(valid)*100)
