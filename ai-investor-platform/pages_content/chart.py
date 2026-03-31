import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from groq import Groq
import os
import ta

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

POPULAR = [
    "RELIANCE", "TCS", "INFY", "HDFCBANK", "SBIN",
    "WIPRO", "ICICIBANK", "MARUTI", "TITAN", "ITC"
]

# ── Symbol normalizer ──────────────────────────────────────────
SYMBOL_MAP = {
    "TATA MOTORS": "TATAMOTORS",
    "TATAMOTORS": "TATAMOTORS",
    "TATA STEEL": "TATASTEEL",
    "TATASTEEL": "TATASTEEL",
    "TATA POWER": "TATAPOWER",
    "TATA CONSULTANCY": "TCS",
    "HDFC BANK": "HDFCBANK",
    "HDFC": "HDFCBANK",
    "ICICI BANK": "ICICIBANK",
    "KOTAK": "KOTAKBANK",
    "KOTAK BANK": "KOTAKBANK",
    "SBI": "SBIN",
    "STATE BANK": "SBIN",
    "BAJAJ FINANCE": "BAJFINANCE",
    "BAJAJ AUTO": "BAJAJ-AUTO",
    "HERO": "HEROMOTOCO",
    "HERO MOTOCORP": "HEROMOTOCO",
    "ASIAN PAINTS": "ASIANPAINT",
    "ULTRATECH": "ULTRACEMCO",
    "ULTRA CEMENT": "ULTRACEMCO",
    "SUN PHARMA": "SUNPHARMA",
    "SUNPHARMA": "SUNPHARMA",
    "ADANI": "ADANIENT",
    "ADANI ENT": "ADANIENT",
    "ADANI PORTS": "ADANIPORTS",
    "MAHINDRA": "M&M",
    "M AND M": "M&M",
    "NESTLE": "NESTLEIND",
    "HUL": "HINDUNILVR",
    "HINDUSTAN UNILEVER": "HINDUNILVR",
    "DR REDDY": "DRREDDY",
    "DR. REDDY": "DRREDDY",
    "TECH MAHINDRA": "TECHM",
    "L&T": "LT",
    "LARSEN": "LT",
    "INDUSIND": "INDUSINDBK",
    "INDUSIND BANK": "INDUSINDBK",
    "POWER GRID": "POWERGRID",
    "DIVIS": "DIVISLAB",
    "DIVI": "DIVISLAB",
    "BAJAJ FINSERV": "BAJAJFINSV",
    "AXIS BANK": "AXISBANK",
    "AXIS": "AXISBANK",
    "COAL INDIA": "COALINDIA",
    "JSPL": "JINDALSTEL",
    "JINDAL": "JINDALSTEL",
    "HAVELLS": "HAVELLS",
    "PIDILITE": "PIDILITIND",
    "BERGER": "BERGEPAINT",
    "BERGER PAINTS": "BERGEPAINT",
    "GODREJ": "GODREJCP",
    "GODREJ CONSUMER": "GODREJCP",
    "DABUR": "DABUR",
    "MARICO": "MARICO",
    "COLGATE": "COLPAL",
    "COLGATE PALMOLIVE": "COLPAL",
    "AMBUJA": "AMBUJACEM",
    "AMBUJA CEMENT": "AMBUJACEM",
    "ACC": "ACC",
    "SHREE CEMENT": "SHREECEM",
    "DLF": "DLF",
    "TRENT": "TRENT",
    "ZOMATO": "ZOMATO",
    "PAYTM": "PAYTM",
    "NYKAA": "FSN",
    "POLICYBAZAAR": "POLICYBZR",
}

def normalize_symbol(raw: str) -> str:
    # Remove .NS or .BSE suffix if user typed it
    cleaned = raw.strip().upper()
    cleaned = cleaned.replace(".NS", "").replace(".BSE", "").strip()
    return SYMBOL_MAP.get(cleaned, cleaned)

# ── Fetch + Indicators ─────────────────────────────────────────
def get_stock_data(ticker):
    try:
        symbol = normalize_symbol(ticker)
        df = yf.Ticker(f"{symbol}.NS").history(period="6mo")
        if df is None or df.empty:
            return None, symbol
        df = df.copy()
        df['MA20'] = df['Close'].rolling(20).mean()
        df['MA50'] = df['Close'].rolling(50).mean()
        df['RSI'] = ta.momentum.RSIIndicator(df['Close'], 14).rsi()
        bb = ta.volatility.BollingerBands(df['Close'], 20)
        df['BB_upper'] = bb.bollinger_hband()
        df['BB_lower'] = bb.bollinger_lband()
        return df, symbol
    except:
        return None, ticker

# ── Main Chart ─────────────────────────────────────────────────
def build_main_chart(df, ticker):
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        row_heights=[0.6, 0.2, 0.2],
        vertical_spacing=0.04,
        subplot_titles=(f"{ticker} Price", "Volume", "RSI")
    )

    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df['Open'], high=df['High'],
        low=df['Low'], close=df['Close'],
        name="Price",
        increasing_line_color='#3fb950',
        decreasing_line_color='#f85149',
        showlegend=False
    ), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=df.index, y=df['MA20'],
        line=dict(color='#58a6ff', width=1.5), name='MA20'
    ), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=df.index, y=df['MA50'],
        line=dict(color='#d29922', width=1.5), name='MA50'
    ), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=df.index, y=df['BB_upper'],
        line=dict(color='#8b949e', width=1, dash='dash'),
        name='BB Upper', showlegend=False
    ), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=df.index, y=df['BB_lower'],
        line=dict(color='#8b949e', width=1, dash='dash'),
        fill='tonexty', fillcolor='rgba(139,148,158,0.07)',
        name='BB Lower', showlegend=False
    ), row=1, col=1)

    colors = [
        '#3fb950' if c >= o else '#f85149'
        for c, o in zip(df['Close'], df['Open'])
    ]
    fig.add_trace(go.Bar(
        x=df.index, y=df['Volume'],
        marker_color=colors, name='Volume', showlegend=False
    ), row=2, col=1)

    fig.add_trace(go.Scatter(
        x=df.index, y=df['RSI'],
        line=dict(color='#a371f7', width=2),
        name='RSI', showlegend=False
    ), row=3, col=1)

    fig.add_hline(y=70, line_dash="dash",
                  line_color="#f85149", line_width=1, row=3, col=1)
    fig.add_hline(y=30, line_dash="dash",
                  line_color="#3fb950", line_width=1, row=3, col=1)

    fig.update_layout(
        paper_bgcolor='#0d1117', plot_bgcolor='#161b22',
        font=dict(color='#e6edf3'),
        xaxis_rangeslider_visible=False,
        height=620,
        margin=dict(l=0, r=0, t=40, b=0),
        legend=dict(bgcolor='#161b22', bordercolor='#30363d',
                    orientation='h', y=1.02)
    )
    for i in range(1, 4):
        fig.update_xaxes(gridcolor='#21262d', showgrid=True, row=i, col=1)
        fig.update_yaxes(gridcolor='#21262d', showgrid=True, row=i, col=1)

    return fig

# ── Pattern Detection ──────────────────────────────────────────
def detect_patterns(df):
    if df is None or df.empty:
        return [], "NEUTRAL"

    latest = df.iloc[-1]
    prev   = df.iloc[-2]
    patterns = []

    rsi  = latest['RSI'] if not pd.isna(latest['RSI']) else 50
    ma20 = latest['MA20']
    ma50 = latest['MA50']
    price = latest['Close']

    if rsi >= 70:
        patterns.append(("warning", "RSI Overbought",
                         f"RSI {round(rsi,1)} — possible pullback",
                         "Wait before buying"))
    elif rsi <= 30:
        patterns.append(("opportunity", "RSI Oversold",
                         f"RSI {round(rsi,1)} — possible bounce",
                         "Watch for reversal"))
    else:
        patterns.append(("neutral", "RSI Neutral",
                         f"RSI {round(rsi,1)} — normal range",
                         "Monitor other signals"))

    if not any(pd.isna(v) for v in [ma20, ma50, prev['MA20'], prev['MA50']]):
        if prev['MA20'] <= prev['MA50'] and ma20 > ma50:
            patterns.append(("opportunity", "Golden Cross",
                             "MA20 crossed above MA50",
                             "Strong bullish signal — consider entry"))
        elif prev['MA20'] >= prev['MA50'] and ma20 < ma50:
            patterns.append(("warning", "Death Cross",
                             "MA20 crossed below MA50",
                             "Bearish — wait for recovery"))
        elif ma20 > ma50:
            patterns.append(("opportunity", "Bullish Trend",
                             f"MA20 ₹{round(ma20,1)} > MA50 ₹{round(ma50,1)}",
                             "Uptrend intact — hold or buy on dips"))
        else:
            patterns.append(("warning", "Bearish Trend",
                             f"MA20 ₹{round(ma20,1)} < MA50 ₹{round(ma50,1)}",
                             "Downtrend — wait before buying"))

    bb_u = latest['BB_upper']
    bb_l = latest['BB_lower']
    if not any(pd.isna(v) for v in [bb_u, bb_l]):
        if price >= bb_u * 0.98:
            patterns.append(("warning", "Near BB Upper Band",
                             "Price near upper band — stretched",
                             "Possible resistance — watch for pullback"))
        elif price <= bb_l * 1.02:
            patterns.append(("opportunity", "Near BB Lower Band",
                             "Price near lower band — support zone",
                             "Possible bounce — watch for entry"))

    opps  = sum(1 for p in patterns if p[0] == "opportunity")
    warns = sum(1 for p in patterns if p[0] == "warning")
    overall = "BULLISH" if opps > warns else "BEARISH" if warns > opps else "NEUTRAL"

    return patterns, overall

# ── AI Explanation ─────────────────────────────────────────────
def get_ai_explanation(ticker, patterns, price, change_pct):
    pattern_text = "\n".join([f"- {p[1]}: {p[2]}" for p in patterns])
    prompt = f"""
Stock: {ticker}, Price: ₹{price}, 6M Change: {change_pct}%
Patterns:\n{pattern_text}

Reply ONLY in this exact JSON format, nothing else:
{{
  "trend": "Bullish" or "Bearish" or "Neutral",
  "recommendation": "Buy" or "Hold" or "Avoid" or "Watch",
  "risk": "Low" or "Medium" or "High",
  "momentum": "one short sentence about price momentum",
  "key_observation": "one short sentence about most important pattern",
  "what_to_watch": "one short sentence about what to monitor next"
}}
"""
    r = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=200, temperature=0.2
    )
    return r.choices[0].message.content


def render_ai_summary(raw_text):
    import json, re
    try:
        match = re.search(r'\{.*\}', raw_text, re.DOTALL)
        if not match:
            st.warning("Could not parse AI response.")
            return
        data = json.loads(match.group())
    except Exception:
        st.warning("AI response format error. Try again.")
        return

    trend   = data.get("trend", "Neutral")
    rec     = data.get("recommendation", "Watch")
    risk    = data.get("risk", "Medium")
    momentum= data.get("momentum", "")
    key_obs = data.get("key_observation", "")
    watch   = data.get("what_to_watch", "")

    trend_color = "#3fb950" if trend=="Bullish" else "#f85149" if trend=="Bearish" else "#d29922"
    rec_color   = "#3fb950" if rec=="Buy" else "#f85149" if rec=="Avoid" else "#d29922"
    risk_color  = "#f85149" if risk=="High" else "#d29922" if risk=="Medium" else "#3fb950"
    trend_icon  = "📈" if trend=="Bullish" else "📉" if trend=="Bearish" else "➡️"
    rec_icon    = "✅" if rec=="Buy" else "❌" if rec=="Avoid" else "⏳"
    risk_icon   = "🔴" if risk=="High" else "🟡" if risk=="Medium" else "🟢"

    c1, c2, c3 = st.columns(3)
    for col, icon, label, val, color in [
        (c1, trend_icon, "TREND", trend, trend_color),
        (c2, rec_icon, "RECOMMENDATION", rec, rec_color),
        (c3, risk_icon, "RISK LEVEL", risk, risk_color),
    ]:
        with col:
            st.markdown(f"""
            <div style="background:#161b22;border:1px solid #30363d;
            border-top:3px solid {color};border-radius:10px;
            padding:16px;text-align:center">
                <div style="font-size:1.6rem">{icon}</div>
                <div style="font-size:0.75rem;color:#8b949e;margin:4px 0">{label}</div>
                <div style="font-size:1.2rem;font-weight:700;color:{color}">{val}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    d1, d2, d3 = st.columns(3)
    for col, color, label, text in [
        (d1, "#58a6ff", "⚡ MOMENTUM", momentum),
        (d2, "#a371f7", "🔍 KEY OBSERVATION", key_obs),
        (d3, "#d29922", "👁️ WHAT TO WATCH", watch),
    ]:
        with col:
            st.markdown(f"""
            <div style="background:#161b22;border:1px solid #30363d;
            border-radius:10px;padding:14px;min-height:100px">
                <div style="font-size:0.75rem;color:{color};
                font-weight:600;margin-bottom:6px">{label}</div>
                <div style="font-size:0.85rem;color:#e6edf3;
                line-height:1.6">{text}</div>
            </div>""", unsafe_allow_html=True)

# ── Page ───────────────────────────────────────────────────────
def show_chart():
    st.markdown("# 📊 Chart Pattern Intelligence")
    st.markdown("*Enter any NSE stock — AI detects patterns and explains in plain English*")
    st.divider()

    for key, val in [("chart_df", None), ("chart_ticker", None), ("chart_ai", None)]:
        if key not in st.session_state:
            st.session_state[key] = val

    c1, c2 = st.columns([2, 1])
    with c1:
        ticker_input = st.text_input(
            "NSE Stock Symbol",
            placeholder="e.g. RELIANCE, TCS, TATA MOTORS, HDFC BANK"
        )
    with c2:
        st.markdown("<br>", unsafe_allow_html=True)
        go_btn = st.button("📊 Analyze", use_container_width=True)

    st.markdown("**Quick select:**")
    cols_a = st.columns(5)
    cols_b = st.columns(5)
    for i, s in enumerate(POPULAR[:5]):
        with cols_a[i]:
            if st.button(s, key=f"qs_a_{s}"):
                st.session_state.chart_ticker = s
                st.session_state.chart_df = None
                st.session_state.chart_ai = None
                st.rerun()
    for i, s in enumerate(POPULAR[5:]):
        with cols_b[i]:
            if st.button(s, key=f"qs_b_{s}"):
                st.session_state.chart_ticker = s
                st.session_state.chart_df = None
                st.session_state.chart_ai = None
                st.rerun()

    if go_btn:
        if not ticker_input.strip():
            st.warning("Please enter a stock symbol.")
        else:
            st.session_state.chart_ticker = ticker_input.strip()
            st.session_state.chart_df = None
            st.session_state.chart_ai = None

    # Fetch
    if st.session_state.chart_ticker and st.session_state.chart_df is None:
        raw = st.session_state.chart_ticker
        with st.spinner(f"Fetching data for {raw}..."):
            df, clean_symbol = get_stock_data(raw)
            if df is None or df.empty:
                st.error(
                    f"No data found for **'{raw}'**. "
                    f"Try the exact NSE symbol e.g. TATAMOTORS, HDFCBANK, BAJFINANCE"
                )
                st.session_state.chart_ticker = None
            else:
                st.session_state.chart_df = df
                st.session_state.chart_ticker = clean_symbol  # use clean symbol

    # Render
    if st.session_state.chart_df is not None:
        df     = st.session_state.chart_df
        ticker = st.session_state.chart_ticker

        price  = round(df['Close'].iloc[-1], 2)
        start  = round(df['Close'].iloc[0], 2)
        change = round(((price - start) / start) * 100, 2)
        high6m = round(df['High'].max(), 2)
        low6m  = round(df['Low'].min(), 2)
        rsi_val= round(df['RSI'].iloc[-1], 1)

        patterns, overall = detect_patterns(df)

        ov_color = "#3fb950" if overall=="BULLISH" else "#f85149" if overall=="BEARISH" else "#d29922"
        st.markdown(f"""
        <div style="text-align:center;margin:12px 0">
            <span style="background:{ov_color}22;color:{ov_color};
            padding:6px 24px;border-radius:30px;font-size:1rem;
            font-weight:700;border:1px solid {ov_color}">
                Overall Signal: {overall}
            </span>
        </div>""", unsafe_allow_html=True)

        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("Price", f"₹{price:,}")
        m2.metric("6M Change", f"{change}%", delta=f"{change}%")
        m3.metric("6M High", f"₹{high6m:,}")
        m4.metric("6M Low", f"₹{low6m:,}")
        m5.metric("RSI", rsi_val)

        st.plotly_chart(build_main_chart(df, ticker),
                        use_container_width=True, key="main_chart")
        st.divider()

        st.markdown("### 🔍 Detected Patterns")
        opp_count  = sum(1 for p in patterns if p[0]=="opportunity")
        warn_count = sum(1 for p in patterns if p[0]=="warning")
        st.markdown(f"""
        <div style="background:#161b22;border:1px solid #30363d;
        border-radius:8px;padding:10px 16px;margin-bottom:12px;
        font-size:0.85rem;color:#8b949e">
            {len(patterns)} patterns detected —
            <span style="color:#3fb950">{opp_count} opportunity</span> ·
            <span style="color:#f85149">{warn_count} warning</span>
        </div>""", unsafe_allow_html=True)

        for p_type, p_name, p_detail, p_action in patterns:
            icon  = "🟢" if p_type=="opportunity" else "🔴" if p_type=="warning" else "🟡"
            color = "#3fb950" if p_type=="opportunity" else "#f85149" if p_type=="warning" else "#d29922"
            st.markdown(f"""
            <div style="background:#161b22;border-left:3px solid {color};
            border-radius:8px;padding:12px 16px;margin-bottom:8px">
                <div style="font-weight:600;color:{color};margin-bottom:4px">
                    {icon} {p_name}</div>
                <div style="font-size:0.88rem;color:#8b949e;margin-bottom:4px">
                    {p_detail}</div>
                <div style="font-size:0.88rem;color:#e6edf3">💡 {p_action}</div>
            </div>""", unsafe_allow_html=True)

        st.divider()
        st.markdown("### 🤖 AI Analysis")
        if st.button("🧠 Get AI Explanation", use_container_width=True):
            with st.spinner("Analyzing patterns..."):
                try:
                    st.session_state.chart_ai = get_ai_explanation(
                        ticker, patterns, price, change
                    )
                except Exception as e:
                    st.error(f"AI error: {str(e)}")

        if st.session_state.chart_ai:
            render_ai_summary(st.session_state.chart_ai)