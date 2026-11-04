import streamlit as st
import streamlit.components.v1 as components
import math, sqlite3, os
from datetime import datetime, date

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(APP_DIR, 'terminal.db')

st.set_page_config(page_title='Options Intelligence Terminal', page_icon='◈', layout='wide', initial_sidebar_state='collapsed')

st.markdown('''
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Manrope:wght@400;500;600;700;800&display=swap');
:root{--bg:#080d13;--panel:#101923;--panel2:#0c141d;--line:#1d2a36;--muted:#81909e;--text:#e8eef4;--gold:#d8b36a;--green:#36c995;--red:#ff6878;--blue:#70a9ff}
html,body,[class*="css"]{font-family:'Manrope',sans-serif;background:var(--bg);color:var(--text)}
.stApp{background:radial-gradient(ellipse at 15% 0%,#172333 0%,#080d13 42%)}
.block-container{padding-top:1.35rem;padding-bottom:2rem;max-width:1600px}
header[data-testid="stHeader"]{background:transparent}
section[data-testid="stSidebar"]{background:#0b131c}
.topline{display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid var(--line);padding:0 0 16px;margin-bottom:18px}
.brand{font-weight:800;letter-spacing:.13em;font-size:18px}.brand span{color:var(--gold)}
.kicker{color:var(--muted);font-family:'DM Mono';font-size:10px;letter-spacing:.18em}
.panel{background:linear-gradient(145deg,#111c27,#0d151e);border:1px solid var(--line);border-radius:14px;padding:16px 18px;min-height:100%}
.metric-label{font-size:10px;color:var(--muted);letter-spacing:.14em;font-family:'DM Mono';text-transform:uppercase}
.metric-value{font-size:27px;font-weight:800;letter-spacing:-.04em;margin-top:6px}
.metric-sub{font-size:11px;color:var(--muted);margin-top:3px}
.section-title{font-size:13px;font-weight:800;letter-spacing:.11em;text-transform:uppercase;color:#cbd5df;margin:4px 0 12px}
.pill{display:inline-block;padding:5px 9px;border-radius:30px;font:11px 'DM Mono';border:1px solid var(--line);color:var(--muted)}
.good{color:var(--green)!important}.bad{color:var(--red)!important}.gold{color:var(--gold)!important}
.rule{border-top:1px solid var(--line);margin:12px 0}
.stButton>button{background:#d8b36a;color:#10151b;border:0;border-radius:8px;font-weight:800;min-height:42px}
.stButton>button:hover{background:#edca83;color:#10151b}
div[data-testid="stTabs"] button{font-weight:700;color:#aebbc8}
div[data-testid="stTabs"] button[aria-selected="true"]{color:var(--gold);border-bottom-color:var(--gold)}
.stTextInput input,.stNumberInput input,.stSelectbox div[data-baseweb="select"]{background:#0b141d;color:var(--text);border-color:var(--line)}
[data-testid="stDataFrame"]{border:1px solid var(--line);border-radius:10px}
.small-note{font-size:11px;color:var(--muted);line-height:1.6}
footer{visibility:hidden}
</style>
''', unsafe_allow_html=True)

# Database: local discipline journal
con = sqlite3.connect(DB, check_same_thread=False)
con.execute('CREATE TABLE IF NOT EXISTS trades (id INTEGER PRIMARY KEY, trade_date TEXT, instrument TEXT, setup TEXT, side TEXT, entry REAL, stop REAL, target REAL, qty INTEGER, status TEXT, pnl REAL DEFAULT 0, note TEXT)')
con.commit()

def card(label, value, sub='', cls=''):
    st.markdown(f'''<div class="panel"><div class="metric-label">{label}</div><div class="metric-value {cls}">{value}</div><div class="metric-sub">{sub}</div></div>''', unsafe_allow_html=True)

def norm_cdf(x): return (1.0 + math.erf(x / math.sqrt(2.0))) / 2.0

def bs_greeks(S,K,T,r,sigma,kind):
    if min(S,K,T,sigma) <= 0: return None
    d1=(math.log(S/K)+(r+0.5*sigma*sigma)*T)/(sigma*math.sqrt(T))
    d2=d1-sigma*math.sqrt(T)
    pdf=math.exp(-0.5*d1*d1)/math.sqrt(2*math.pi)
    delta=norm_cdf(d1) if kind=='CE' else norm_cdf(d1)-1
    gamma=pdf/(S*sigma*math.sqrt(T))
    vega=S*pdf*math.sqrt(T)/100
    theta_year=-(S*pdf*sigma)/(2*math.sqrt(T)) - r*K*math.exp(-r*T)*norm_cdf(d2) if kind=='CE' else -(S*pdf*sigma)/(2*math.sqrt(T)) + r*K*math.exp(-r*T)*norm_cdf(-d2)
    theta_day=theta_year/365
    return delta,gamma,theta_day,vega

st.markdown('''<div class="topline"><div><div class="brand">◈ <span>OPTIONS</span> INTELLIGENCE</div><div class="kicker">NIFTY · SENSEX / BUYER'S DECISION TERMINAL</div></div><div style="text-align:right"><div class="kicker">LOCAL WORKSPACE · ₹0 SOFTWARE</div><div class="pill">● MANUAL / CHART MODE</div></div></div>''', unsafe_allow_html=True)

# top strip
trades_today = con.execute('SELECT COUNT(*) FROM trades WHERE trade_date=?', (date.today().isoformat(),)).fetchone()[0]
closed_today = con.execute("SELECT COUNT(*) FROM trades WHERE trade_date=? AND status='Closed'", (date.today().isoformat(),)).fetchone()[0]
remaining=max(0,2-trades_today)
c1,c2,c3,c4=st.columns(4)
with c1: card('Session','NSE / BSE','Local dashboard')
with c2: card('Daily trade slots',f'{remaining} / 2','Remaining planned entries', 'good' if remaining else 'bad')
with c3: card('Risk mode','PROTECT','No revenge · No overtrading','gold')
with c4: card('Data status','NOT CONNECTED','No fake live prices displayed','bad')

st.markdown('<div class="small-note" style="margin:10px 2px 16px">This first build is a working interface and analysis workspace. Charts are embedded from TradingView. The app does not claim to receive live NSE option-chain data until an authorized free feed is connected.</div>',unsafe_allow_html=True)

tabs=st.tabs(['MARKET DESK','SETUP CHECK','OPTION GREEKS','RISK & JOURNAL'])

with tabs[0]:
    left,right=st.columns([1.65,1])
    with left:
        st.markdown('<div class="section-title">Market charts · TradingView</div>',unsafe_allow_html=True)
        market=st.segmented_control('Select index', ['NIFTY','SENSEX'], default='NIFTY', key='market_select')
        symbol='NSE:NIFTY' if market=='NIFTY' else 'BSE:SENSEX'
        components.html(f'''<div class="tradingview-widget-container" style="height:560px;width:100%"><div id="tv_chart" style="height:540px;width:100%"></div><script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script><script>new TradingView.widget({{"autosize":true,"symbol":"{symbol}","interval":"5","timezone":"Asia/Kolkata","theme":"dark","style":"1","locale":"en","enable_publishing":false,"hide_top_toolbar":false,"hide_legend":false,"save_image":false,"container_id":"tv_chart","backgroundColor":"#0d151e","gridColor":"rgba(255,255,255,0.04)"}});</script></div>''',height=565)
    with right:
        st.markdown('<div class="section-title">Market context · manual confirmation</div>',unsafe_allow_html=True)
        direction=st.selectbox('Market regime',['Not assessed','Uptrend','Downtrend','Sideways / Range'])
        vwap=st.selectbox('Price vs VWAP',['Not checked','Above VWAP','Below VWAP','Chopping around VWAP'])
        structure=st.selectbox('Price structure',['Not checked','Higher High + Higher Low','Lower High + Lower Low','Inside range'])
        breadth=st.selectbox('Market participation',['Not checked','Broad participation','Weak / mixed participation'])
        st.markdown('<div class="rule"></div>',unsafe_allow_html=True)
        if direction=='Not assessed' or vwap=='Not checked' or structure=='Not checked':
            st.info('Complete market context before considering a setup.')
        elif direction=='Uptrend' and vwap=='Above VWAP' and structure=='Higher High + Higher Low':
            st.success('BIAS: BULLISH · Wait for your defined setup. Not an entry signal.')
        elif direction=='Downtrend' and vwap=='Below VWAP' and structure=='Lower High + Lower Low':
            st.error('BIAS: BEARISH · Wait for your defined setup. Not an entry signal.')
        else:
            st.warning('BIAS: MIXED / RANGE · Avoid forcing an options-buying trade.')
        st.caption('Regime is based on your selected observations, not automatically read from the chart.')

with tabs[1]:
    st.markdown('<div class="section-title">Only your two approved setups</div>',unsafe_allow_html=True)
    a,b=st.columns(2)
    with a:
        st.markdown('<div class="panel"><div class="metric-label">SETUP 01</div><div class="metric-value" style="font-size:22px">Support / Resistance</div><div class="metric-sub">Breakout or rejection</div></div>',unsafe_allow_html=True)
        sr=st.selectbox('S/R event',['Not formed','Breakout','Rejection','Failed breakout'],key='sr')
        close=st.checkbox('5-minute candle closed at / beyond the level',key='srclose')
        retest=st.checkbox('Retest / rejection confirmed',key='srtest')
        vol=st.checkbox('Volume supports the move',key='srvol')
    with b:
        st.markdown('<div class="panel"><div class="metric-label">SETUP 02</div><div class="metric-value" style="font-size:22px">Trendline Breakout</div><div class="metric-sub">Break + close + follow-through</div></div>',unsafe_allow_html=True)
        tl=st.selectbox('Trendline event',['Not formed','Upside breakout','Downside breakout','False breakout'],key='tl')
        tlclose=st.checkbox('Candle closed beyond trendline',key='tlclose')
        follow=st.checkbox('Follow-through / retest confirmed',key='tlfollow')
        tlvol=st.checkbox('Volume supports the move',key='tlvol')
    st.markdown('<div class="rule"></div>',unsafe_allow_html=True)
    oi=st.checkbox('OI / price behaviour is supportive')
    premium=st.checkbox('Option spread and liquidity are acceptable')
    ivok=st.checkbox('IV is not showing an adverse collapse')
    riskok=st.checkbox('Stop-loss and position size are defined before entry')
    chosen = (sr in ['Breakout','Rejection'] and close and (retest or vol)) or (tl in ['Upside breakout','Downside breakout'] and tlclose and (follow or tlvol))
    confirmations=sum([oi,premium,ivok,riskok])
    if chosen and confirmations==4:
        st.success('SETUP CHECK: READY FOR YOUR OWN FINAL REVIEW. This is not an order instruction.')
    elif chosen:
        st.warning(f'SETUP FOUND · {confirmations}/4 additional checks complete. Wait; do not force entry.')
    else:
        st.info('NO TRADE · Wait for Support/Resistance or Trendline Breakout confirmation.')

with tabs[2]:
    st.markdown('<div class="section-title">Option Greeks calculator · Black–Scholes estimate</div>',unsafe_allow_html=True)
    st.caption('Enter the option inputs manually. European-style approximation; actual exchange Greeks, IV and market prices may differ.')
    x1,x2,x3=st.columns(3)
    with x1: S=st.number_input('Underlying price',min_value=0.0,value=24000.0,step=50.0)
    with x2: K=st.number_input('Strike price',min_value=0.0,value=24000.0,step=50.0)
    with x3: kind=st.selectbox('Option type',['CE','PE'])
    x4,x5,x6=st.columns(3)
    with x4: iv=st.number_input('Implied volatility (%)',min_value=0.1,max_value=300.0,value=15.0,step=0.5)
    with x5: days=st.number_input('Days to expiry',min_value=0.01,value=1.0,step=0.25)
    with x6: rate=st.number_input('Risk-free rate (%)',min_value=0.0,max_value=20.0,value=6.5,step=0.25)
    if st.button('Calculate Greeks',key='greeks'):
        g=bs_greeks(S,K,days/365,rate/100,iv/100,kind)
        if g:
            g1,g2,g3,g4=st.columns(4)
            with g1: card('Delta',f'{g[0]:.3f}','Per 1-point underlying move')
            with g2: card('Gamma',f'{g[1]:.5f}','Delta change per point')
            with g3: card('Theta / day',f'{g[2]:.2f}','Approx. premium decay', 'bad' if g[2]<0 else 'good')
            with g4: card('Vega / 1 IV pt',f'{g[3]:.2f}','Approx. premium sensitivity')
        else: st.error('Enter valid positive inputs.')

with tabs[3]:
    st.markdown('<div class="section-title">Capital protection · trade journal</div>',unsafe_allow_html=True)
    with st.form('trade_form'):
        q1,q2,q3=st.columns(3)
        with q1: inst=st.selectbox('Index',['NIFTY','SENSEX'])
        with q2: setup=st.selectbox('Setup',['Support / Resistance','Trendline Breakout'])
        with q3: side=st.selectbox('Side',['CE','PE'])
        q4,q5,q6=st.columns(3)
        with q4: entry=st.number_input('Option entry premium',min_value=0.0,value=100.0,step=1.0)
        with q5: stop=st.number_input('Stop-loss premium',min_value=0.0,value=90.0,step=1.0)
        with q6: target=st.number_input('Target premium',min_value=0.0,value=120.0,step=1.0)
        q7,q8=st.columns(2)
        with q7: qty=st.number_input('Total quantity (units)',min_value=1,value=65,step=1)
        with q8: note=st.text_input('Reason / note','')
        save=st.form_submit_button('Log planned trade')
        if save:
            if trades_today>=2: st.error('Daily limit reached. No more trades today.')
            elif entry<=stop or target<=entry: st.error('For a long option, require Stop < Entry < Target.')
            elif (entry-stop)*qty>1000: st.error(f'Risk exceeds ₹1,000. Planned risk: ₹{(entry-stop)*qty:,.0f}.')
            else:
                con.execute('INSERT INTO trades(trade_date,instrument,setup,side,entry,stop,target,qty,status,note) VALUES(?,?,?,?,?,?,?,?,?,?)',(date.today().isoformat(),inst,setup,side,entry,stop,target,int(qty),'Open',note)); con.commit(); st.success('Trade logged locally. Daily trade slot used.')
    rows=con.execute('SELECT id,trade_date,instrument,setup,side,entry,stop,target,qty,status,pnl,note FROM trades ORDER BY id DESC LIMIT 30').fetchall()
    if rows:
        import pandas as pd
        df=pd.DataFrame(rows,columns=['ID','Date','Index','Setup','Side','Entry','SL','Target','Qty','Status','P&L','Note'])
        st.dataframe(df,use_container_width=True,hide_index=True)
        ids=[r[0] for r in rows if r[9]=='Open']
        if ids:
            selected=st.selectbox('Close a logged trade',ids)
            p1,p2=st.columns(2)
            with p1: pnl=st.number_input('Realized P&L (₹)',value=0.0,step=50.0)
            with p2:
                if st.button('Mark trade closed'):
                    con.execute("UPDATE trades SET status='Closed',pnl=? WHERE id=?",(pnl,selected)); con.commit(); st.rerun()
    else: st.caption('No trades logged yet. Your journal is stored locally on this laptop.')
    st.markdown('<div class="small-note">Risk calculation excludes brokerage, taxes, slippage and gaps. Use actual lot size and include all charges before placing any order. This app does not place orders.</div>',unsafe_allow_html=True)

st.markdown('<div style="border-top:1px solid #1d2a36;margin-top:22px;padding-top:12px;display:flex;justify-content:space-between"><span class="kicker">PLAN · WAIT · EXECUTE · PROTECT</span><span class="kicker">LOCAL BUILD · NO AUTO-TRADING</span></div>',unsafe_allow_html=True)
