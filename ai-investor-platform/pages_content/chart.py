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

SYMBOL_MAP = {
    "TATA MOTORS": "TATAMOTORS", "TATAMOTORS": "TATAMOTORS",
    "TATA STEEL": "TATASTEEL", "TATASTEEL": "TATASTEEL",
    "TATA POWER": "TATAPOWER", "TATA CONSULTANCY": "TCS",
    "HDFC BANK": "HDFCBANK", "HDFC": "HDFCBANK",
    "ICICI BANK": "ICICIBANK", "KOTAK": "KOTAKBANK",
    "KOTAK BANK": "KOTAKBANK", "SBI": "SBIN",
    "STATE BANK": "SBIN", "BAJAJ FINANCE": "BAJFINANCE",
    "BAJAJ AUTO": "BAJAJ-AUTO", "HERO": "HEROMOTOCO",
    "HERO MOTOCORP": "HEROMOTOCO", "ASIAN PAINTS": "ASIANPAINT",
    "ULTRATECH": "ULTRACEMCO", "SUN PHARMA": "SUNPHARMA",
    "SUNPHARMA": "SUNPHARMA", "ADANI": "ADANIENT",
    "ADANI ENT": "ADANIENT", "ADANI PORTS": "ADANIPORTS",
    "MAHINDRA": "M&M", "M AND M": "M&M", "NESTLE": "NESTLEIND",
    "HUL": "HINDUNILVR", "HINDUSTAN UNILEVER": "HINDUNILVR",
    "DR REDDY": "DRREDDY", "DR. REDDY": "DRREDDY",
    "TECH MAHINDRA": "TECHM", "L&T": "LT", "LARSEN": "LT",
    "INDUSIND": "INDUSINDBK", "INDUSIND BANK": "INDUSINDBK",
    "POWER GRID": "POWERGRID", "DIVIS": "DIVISLAB",
    "BAJAJ FINSERV": "BAJAJFINSV", "AXIS BANK": "AXISBANK",
    "AXIS": "AXISBANK", "COAL INDIA": "COALINDIA",
    "JSPL": "JINDALSTEL", "JINDAL": "JINDALSTEL",
    "PIDILITE": "PIDILITIND", "BERGER": "BERGEPAINT",
    "BERGER PAINTS": "BERGEPAINT", "GODREJ": "GODREJCP",
    "GODREJ CONSUMER": "GODREJCP", "COLGATE": "COLPAL",
    "COLGATE PALMOLIVE": "COLPAL", "AMBUJA": "AMBUJACEM",
    "AMBUJA CEMENT": "AMBUJACEM", "SHREE CEMENT": "SHREECEM",
    "ZOMATO": "ZOMATO", "PAYTM": "PAYTM", "NYKAA": "FSN",
}

TIMEFRAMES = {
    "1M": "1mo", "3M": "3mo", "6M": "6mo", "1Y": "1y"
}

def normalize_symbol(raw: str) -> str:
    cleaned = raw.strip().upper()
    cleaned = cleaned.replace(".NS", "").replace(".BSE", "").strip()
    return SYMBOL_MAP.get(cleaned, cleaned)

def get_stock_data(ticker, period="6mo"):
    try:
        symbol = normalize_symbol(ticker)
        df = yf.Ticker(f"{symbol}.NS").history(period=period)
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

def build_main_chart(df, ticker):
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        row_heights=[0.60, 0.20, 0.20],
        vertical_spacing=0.02,
        subplot_titles=(
            f"<b>{ticker}</b>  Price",
            "<b>Volume</b>",
            "<b>RSI (14)</b>"
        )
    )

    # ── Candlestick ──────────────────────────────────────────
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df['Open'], high=df['High'],
        low=df['Low'],  close=df['Close'],
        name="Price",
        increasing=dict(line=dict(color='#00C853', width=1),
                        fillcolor='#00C853'),
        decreasing=dict(line=dict(color='#FF1744', width=1),
                        fillcolor='#FF1744'),
        showlegend=False,
        whiskerwidth=0.3,
    ), row=1, col=1)

    # ── Bollinger Bands ──────────────────────────────────────
    fig.add_trace(go.Scatter(
        x=df.index, y=df['BB_upper'],
        line=dict(color='rgba(100,120,200,0.6)', width=1, dash='dot'),
        name='BB Upper', showlegend=True, legendgroup='bb'
    ), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=df.index, y=df['BB_lower'],
        line=dict(color='rgba(100,120,200,0.6)', width=1, dash='dot'),
        name='BB Lower', showlegend=False, legendgroup='bb',
        fill='tonexty',
        fillcolor='rgba(100,120,200,0.06)'
    ), row=1, col=1)

    # ── Moving Averages ──────────────────────────────────────
    fig.add_trace(go.Scatter(
        x=df.index, y=df['MA20'],
        line=dict(color='#29B6F6', width=1.5),
        name='MA 20'
    ), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=df.index, y=df['MA50'],
        line=dict(color='#FFA726', width=1.5),
        name='MA 50'
    ), row=1, col=1)

    # ── Volume ───────────────────────────────────────────────
    vol_colors = [
        '#00C853' if c >= o else '#FF1744'
        for c, o in zip(df['Close'], df['Open'])
    ]
    fig.add_trace(go.Bar(
        x=df.index, y=df['Volume'],
        marker_color=vol_colors,
        marker_opacity=0.7,
        name='Volume', showlegend=False
    ), row=2, col=1)

    # ── RSI ───────────────────────────────────────────────────
    fig.add_trace(go.Scatter(
        x=df.index, y=df['RSI'],
        line=dict(color='#CE93D8', width=2),
        name='RSI', showlegend=False
    ), row=3, col=1)

    fig.add_hrect(y0=70, y1=100, row=3, col=1,
                  fillcolor='rgba(255,23,68,0.07)',
                  line_width=0)
    fig.add_hrect(y0=0, y1=30, row=3, col=1,
                  fillcolor='rgba(0,200,83,0.07)',
                  line_width=0)
    fig.add_hline(y=70, line_dash="dash",
                  line_color="rgba(255,23,68,0.5)",
                  line_width=1, row=3, col=1,
                  annotation_text="OB 70",
                  annotation_position="right",
                  annotation_font_color="rgba(255,23,68,0.8)",
                  annotation_font_size=10)
    fig.add_hline(y=30, line_dash="dash",
                  line_color="rgba(0,200,83,0.5)",
                  line_width=1, row=3, col=1,
                  annotation_text="OS 30",
                  annotation_position="right",
                  annotation_font_color="rgba(0,200,83,0.8)",
                  annotation_font_size=10)
    fig.add_hline(y=50, line_dash="dot",
                  line_color="rgba(150,150,150,0.25)",
                  line_width=1, row=3, col=1)

    # ── Layout ────────────────────────────────────────────────
    grid = '#1E2A45'
    fig.update_layout(
        paper_bgcolor='#0A0E1A',
        plot_bgcolor='#0F1629',
        font=dict(color='#CBD5E1', family='monospace', size=11),
        hovermode='x unified',
        hoverlabel=dict(
            bgcolor='#1E2A45',
            bordercolor='#334155',
            font=dict(color='#E2E8F0', size=11)
        ),
        xaxis_rangeslider_visible=False,
        height=680,
        margin=dict(l=10, r=80, t=45, b=10),
        legend=dict(
            bgcolor='rgba(15,22,41,0.8)',
            bordercolor='#1E2A45',
            borderwidth=1,
            orientation='h',
            x=0, y=1.04,
            font=dict(size=11)
        ),
        dragmode='pan',
    )

    # axis styling shared
    axis_style = dict(
        gridcolor=grid,
        gridwidth=0.5,
        showgrid=True,
        zeroline=False,
        showline=True,
        linecolor='#1E2A45',
        tickfont=dict(size=10, color='#94A3B8'),
        tickformat=',.0f',
    )

    fig.update_xaxes(**{k: v for k, v in axis_style.items()
                        if k != 'tickformat'},
                     showticklabels=False, row=1, col=1)
    fig.update_xaxes(**{k: v for k, v in axis_style.items()
                        if k != 'tickformat'},
                     showticklabels=False, row=2, col=1)
    fig.update_xaxes(**{k: v for k, v in axis_style.items()
                        if k != 'tickformat'},
                     showticklabels=True,
                     tickangle=0, row=3, col=1)

    fig.update_yaxes(**axis_style, row=1, col=1, tickprefix='₹')
    fig.update_yaxes(**{k: v for k, v in axis_style.items()
                        if k != 'tickformat'},
                     tickformat='.2s', row=2, col=1)
    fig.update_yaxes(**axis_style, tickprefix='',
                     range=[0, 100], row=3, col=1,
                     tickvals=[0, 30, 50, 70, 100])

    # subplot title styling
    for ann in fig.layout.annotations:
        ann.font.size = 11
        ann.font.color = '#64748B'

    return fig

def detect_patterns(df):
    if df is None or df.empty:
        return [], "NEUTRAL"
    latest = df.iloc[-1]
    prev   = df.iloc[-2]
    patterns = []
    rsi   = latest['RSI'] if not pd.isna(latest['RSI']) else 50
    ma20  = latest['MA20']
    ma50  = latest['MA50']
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
    overall = ("BULLISH" if opps > warns
               else "BEARISH" if warns > opps else "NEUTRAL")
    return patterns, overall

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

    trend    = data.get("trend", "Neutral")
    rec      = data.get("recommendation", "Watch")
    risk     = data.get("risk", "Medium")
    momentum = data.get("momentum", "")
    key_obs  = data.get("key_observation", "")
    watch    = data.get("what_to_watch", "")

    trend_color = ("#00C853" if trend == "Bullish"
                   else "#FF1744" if trend == "Bearish" else "#FFA726")
    rec_color   = ("#00C853" if rec == "Buy"
                   else "#FF1744" if rec == "Avoid" else "#FFA726")
    risk_color  = ("#FF1744" if risk == "High"
                   else "#FFA726" if risk == "Medium" else "#00C853")
    trend_icon  = "📈" if trend == "Bullish" else "📉" if trend == "Bearish" else "➡️"
    rec_icon    = "✅" if rec == "Buy" else "❌" if rec == "Avoid" else "⏳"
    risk_icon   = "🔴" if risk == "High" else "🟡" if risk == "Medium" else "🟢"

    c1, c2, c3 = st.columns(3)
    for col, icon, label, val, color in [
        (c1, trend_icon,  "TREND",          trend, trend_color),
        (c2, rec_icon,    "RECOMMENDATION", rec,   rec_color),
        (c3, risk_icon,   "RISK LEVEL",     risk,  risk_color),
    ]:
        with col:
            st.markdown(f"""
            <div style="background:#0F1629;border:1px solid #1E2A45;
            border-top:3px solid {color};border-radius:10px;
            padding:18px;text-align:center">
                <div style="font-size:1.8rem">{icon}</div>
                <div style="font-size:0.72rem;color:#64748B;
                margin:6px 0;letter-spacing:1px">{label}</div>
                <div style="font-size:1.25rem;font-weight:700;
                color:{color}">{val}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    d1, d2, d3 = st.columns(3)
    for col, color, label, text in [
        (d1, "#29B6F6", "⚡ MOMENTUM",        momentum),
        (d2, "#CE93D8", "🔍 KEY OBSERVATION", key_obs),
        (d3, "#FFA726", "👁️ WHAT TO WATCH",  watch),
    ]:
        with col:
            st.markdown(f"""
            <div style="background:#0F1629;border:1px solid #1E2A45;
            border-radius:10px;padding:14px;min-height:100px">
                <div style="font-size:0.7rem;color:{color};font-weight:700;
                letter-spacing:0.8px;margin-bottom:8px">{label}</div>
                <div style="font-size:0.88rem;color:#CBD5E1;
                line-height:1.7">{text}</div>
            </div>""", unsafe_allow_html=True)

def show_chart():
    st.markdown("# 📊 Chart Pattern Intelligence")
    st.markdown("*Enter any NSE stock — AI detects patterns and explains in plain English*")
    st.divider()

    for key, val in [
        ("chart_df", None), ("chart_ticker", None),
        ("chart_ai", None), ("chart_period", "6mo")
    ]:
        if key not in st.session_state:
            st.session_state[key] = val

    # ── Input row ──────────────────────────────────────────────
    c1, c2 = st.columns([2, 1])
    with c1:
        ticker_input = st.text_input(
            "NSE Stock Symbol",
            placeholder="e.g. RELIANCE, TCS, TATA MOTORS, HDFC BANK"
        )
    with c2:
        st.markdown("<br>", unsafe_allow_html=True)
        go_btn = st.button("📊 Analyze", use_container_width=True)

    # ── Quick select ───────────────────────────────────────────
    st.markdown("**Quick select:**")
    cols_a = st.columns(5)
    cols_b = st.columns(5)
    for i, s in enumerate(POPULAR[:5]):
        with cols_a[i]:
            if st.button(s, key=f"qs_a_{s}"):
                st.session_state.chart_ticker = s
                st.session_state.chart_df     = None
                st.session_state.chart_ai     = None
                st.rerun()
    for i, s in enumerate(POPULAR[5:]):
        with cols_b[i]:
            if st.button(s, key=f"qs_b_{s}"):
                st.session_state.chart_ticker = s
                st.session_state.chart_df     = None
                st.session_state.chart_ai     = None
                st.rerun()

    # ── Timeframe selector ─────────────────────────────────────
    if st.session_state.chart_ticker:
        st.markdown("**Timeframe:**")
        tf_cols = st.columns(4)
        tf_labels = list(TIMEFRAMES.keys())
        for i, label in enumerate(tf_labels):
            with tf_cols[i]:
                period_val = TIMEFRAMES[label]
                is_active  = st.session_state.chart_period == period_val
                btn_style  = (
                    "background:#00D4AA22;color:#00D4AA;"
                    "border:1px solid #00D4AA40;"
                ) if is_active else ""
                if st.button(
                    label,
                    key=f"tf_{label}",
                    use_container_width=True,
                    help=f"Show {label} data"
                ):
                    if st.session_state.chart_period != period_val:
                        st.session_state.chart_period = period_val
                        st.session_state.chart_df     = None
                        st.session_state.chart_ai     = None
                        st.rerun()

    # ── Set ticker from text input ─────────────────────────────
    if go_btn:
        if not ticker_input.strip():
            st.warning("Please enter a stock symbol.")
        else:
            st.session_state.chart_ticker = ticker_input.strip()
            st.session_state.chart_df     = None
            st.session_state.chart_ai     = None

    # ── Fetch ──────────────────────────────────────────────────
    if st.session_state.chart_ticker and st.session_state.chart_df is None:
        raw = st.session_state.chart_ticker
        period = st.session_state.get("chart_period", "6mo")
        with st.spinner(f"Fetching {raw} · {period}..."):
            df, clean_symbol = get_stock_data(raw, period)
            if df is None or df.empty:
                st.error(
                    f"No data for **'{raw}'**. "
                    f"Try exact NSE symbol: TATAMOTORS, HDFCBANK, BAJFINANCE"
                )
                st.session_state.chart_ticker = None
            else:
                st.session_state.chart_df     = df
                st.session_state.chart_ticker = clean_symbol

    # ── Render ─────────────────────────────────────────────────
    if st.session_state.chart_df is not None:
        df     = st.session_state.chart_df
        ticker = st.session_state.chart_ticker
        period = st.session_state.get("chart_period", "6mo")

        price   = round(df['Close'].iloc[-1], 2)
        start   = round(df['Close'].iloc[0], 2)
        change  = round(((price - start) / start) * 100, 2)
        high_p  = round(df['High'].max(), 2)
        low_p   = round(df['Low'].min(), 2)
        rsi_val = round(df['RSI'].iloc[-1], 1)
        vol_avg = int(df['Volume'].mean())

        patterns, overall = detect_patterns(df)

        # Overall signal badge
        ov_color = ("#00C853" if overall == "BULLISH"
                    else "#FF1744" if overall == "BEARISH" else "#FFA726")
        tf_label = [k for k, v in TIMEFRAMES.items()
                    if v == period][0]
        st.markdown(f"""
        <div style="display:flex;align-items:center;
        justify-content:space-between;margin:12px 0">
            <span style="background:{ov_color}18;color:{ov_color};
            padding:6px 22px;border-radius:30px;font-size:0.95rem;
            font-weight:700;border:1px solid {ov_color}55">
                {overall}
            </span>
            <span style="background:#0F1629;color:#64748B;
            padding:5px 16px;border-radius:20px;font-size:0.8rem;
            border:1px solid #1E2A45">
                {ticker} · NSE · {tf_label}
            </span>
        </div>""", unsafe_allow_html=True)

        # Metrics
        m1, m2, m3, m4, m5, m6 = st.columns(6)
        m1.metric("LTP", f"₹{price:,}")
        m2.metric("Change", f"{change}%", delta=f"{change}%")
        m3.metric("High", f"₹{high_p:,}")
        m4.metric("Low",  f"₹{low_p:,}")
        m5.metric("RSI",  rsi_val)
        m6.metric("Avg Vol", f"{vol_avg:,}")

        # Chart
        st.plotly_chart(
            build_main_chart(df, ticker),
            use_container_width=True,
            key="main_chart",
            config={
                'displayModeBar': True,
                'modeBarButtonsToRemove': [
                    'lasso2d', 'select2d', 'autoScale2d'
                ],
                'displaylogo': False,
                'scrollZoom': True,
            }
        )

        # Patterns
        st.divider()
        st.markdown("### 🔍 Detected Patterns")
        opp_c  = sum(1 for p in patterns if p[0] == "opportunity")
        warn_c = sum(1 for p in patterns if p[0] == "warning")
        st.markdown(f"""
        <div style="background:#0F1629;border:1px solid #1E2A45;
        border-radius:8px;padding:10px 16px;margin-bottom:12px;
        font-size:0.85rem;color:#64748B">
            {len(patterns)} patterns detected —
            <span style="color:#00C853">{opp_c} opportunity</span> ·
            <span style="color:#FF1744">{warn_c} warning</span>
        </div>""", unsafe_allow_html=True)

        for p_type, p_name, p_detail, p_action in patterns:
            icon  = ("🟢" if p_type == "opportunity"
                     else "🔴" if p_type == "warning" else "🟡")
            color = ("#00C853" if p_type == "opportunity"
                     else "#FF1744" if p_type == "warning" else "#FFA726")
            st.markdown(f"""
            <div style="background:#0F1629;border-left:3px solid {color};
            border-radius:8px;padding:12px 16px;margin-bottom:8px">
                <div style="font-weight:600;color:{color};
                margin-bottom:4px">{icon} {p_name}</div>
                <div style="font-size:0.88rem;color:#64748B;
                margin-bottom:4px">{p_detail}</div>
                <div style="font-size:0.88rem;color:#CBD5E1">
                    💡 {p_action}</div>
            </div>""", unsafe_allow_html=True)

        # AI section
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