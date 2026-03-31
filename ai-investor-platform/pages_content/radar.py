import streamlit as st
import yfinance as yf
from groq import Groq
import os
import html

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

NSE_STOCKS = [
    "RELIANCE.NS","TCS.NS","HDFCBANK.NS","INFY.NS","ICICIBANK.NS",
    "HINDUNILVR.NS","SBIN.NS","BHARTIARTL.NS","ITC.NS","KOTAKBANK.NS",
    "LT.NS","AXISBANK.NS","ASIANPAINT.NS","MARUTI.NS","WIPRO.NS",
    "ULTRACEMCO.NS","TITAN.NS","BAJFINANCE.NS","NESTLEIND.NS","POWERGRID.NS"
]

# ---------------- DATA ----------------
def fetch_stock_signals(ticker):
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="30d")

        if hist is None or hist.empty or len(hist) < 5:
            return None

        current_price = round(hist['Close'].iloc[-1], 2)
        prev_price = round(hist['Close'].iloc[-6], 2)
        change_5d = round(((current_price - prev_price) / prev_price) * 100, 2)

        avg_vol = hist['Volume'].iloc[:-1].mean()
        curr_vol = hist['Volume'].iloc[-1]
        volume_spike = round((curr_vol / avg_vol) * 100, 1) if avg_vol else 0

        week_high = hist['High'].max()

        signal_score = 0
        signals = []

        if volume_spike > 200:
            signal_score += 3
            signals.append(f"Volume spike {volume_spike}%")
        elif volume_spike > 150:
            signal_score += 2
            signals.append(f"High volume {volume_spike}%")

        if change_5d > 8:
            signal_score += 3
            signals.append(f"Strong rally {change_5d}%")
        elif change_5d > 4:
            signal_score += 2
            signals.append(f"Momentum {change_5d}%")
        elif change_5d < -8:
            signal_score += 2
            signals.append(f"Drop {change_5d}%")

        if ((week_high - current_price) / week_high) * 100 < 2:
            signal_score += 2
            signals.append("Near breakout")

        return {
            "ticker": ticker.replace(".NS", ""),
            "price": current_price,
            "change_5d": change_5d,
            "signal_score": signal_score,
            "signals": signals
        }
    except:
        return None


# ---------------- AI ----------------
def get_ai(stock):
    prompt = f"""
You are a stock analyst. Analyze this Indian stock and respond ONLY in this exact JSON format, nothing else:

{{
  "action": "BUY" or "SELL" or "HOLD",
  "confidence": a number from 1 to 100,
  "reason": "one simple sentence why (max 12 words)",
  "risk": "LOW" or "MEDIUM" or "HIGH",
  "tip": "one plain-English tip for a beginner investor (max 15 words)"
}}

Stock: {stock['ticker']}
Price: ₹{stock['price']}
5-Day Change: {stock['change_5d']}%
Signals: {', '.join(stock['signals'])}

Respond ONLY with the JSON. No extra text.
"""
    res = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=150,
        temperature=0.3
    )
    raw = res.choices[0].message.content.strip()
    # parse JSON safely
    import json, re
    try:
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        return json.loads(match.group()) if match else None
    except:
        return None


# ---------------- VISUAL AI CARD ----------------
def render_ai_result(data):
    if not data:
        st.warning("Could not parse AI response. Try again.")
        return

    action    = data.get("action", "HOLD").upper()
    confidence= data.get("confidence", 50)
    reason    = data.get("reason", "")
    risk      = data.get("risk", "MEDIUM").upper()
    tip       = data.get("tip", "")

    action_color = {"BUY": "#3fb950", "SELL": "#f85149", "HOLD": "#d29922"}.get(action, "#8b949e")
    action_emoji = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}.get(action, "⚪")
    risk_color   = {"LOW": "#3fb950", "MEDIUM": "#d29922", "HIGH": "#f85149"}.get(risk, "#8b949e")
    conf_bar     = min(confidence, 100)

    st.markdown(f"""
    <div style="background:#0d1117;border:1px solid #30363d;border-radius:12px;
    padding:14px;margin-top:6px;margin-bottom:12px">

      <!-- Action badge -->
      <div style="display:flex;align-items:center;gap:10px;margin-bottom:10px">
        <div style="background:{action_color}22;border:1.5px solid {action_color};
        border-radius:8px;padding:4px 14px;font-size:1rem;font-weight:700;
        color:{action_color}">{action_emoji} {action}</div>
        <div style="font-size:0.78rem;color:#8b949e">AI Recommendation</div>
      </div>

      <!-- Confidence bar -->
      <div style="font-size:0.75rem;color:#8b949e;margin-bottom:3px">
        Confidence: <b style="color:#e6edf3">{confidence}%</b>
      </div>
      <div style="background:#21262d;border-radius:4px;height:8px;margin-bottom:10px">
        <div style="background:{action_color};width:{conf_bar}%;height:8px;
        border-radius:4px"></div>
      </div>

      <!-- Reason -->
      <div style="font-size:0.82rem;color:#e6edf3;margin-bottom:8px">
        📌 <b>Why:</b> {html.escape(reason)}
      </div>

      <!-- Risk badge -->
      <div style="margin-bottom:8px">
        <span style="background:{risk_color}22;border:1px solid {risk_color};
        border-radius:6px;padding:2px 10px;font-size:0.75rem;
        color:{risk_color};font-weight:600">⚠️ Risk: {risk}</span>
      </div>

      <!-- Beginner tip -->
      <div style="background:#161b22;border-left:3px solid #58a6ff;
      border-radius:0 8px 8px 0;padding:8px 10px;
      font-size:0.8rem;color:#8b949e">
        💡 <b style="color:#58a6ff">Tip:</b> {html.escape(tip)}
      </div>

    </div>
    """, unsafe_allow_html=True)


# ---------------- CARD ----------------
def render_card(stock, column_type):
    pct   = min((stock['signal_score'] / 8) * 100, 100)
    color = "#3fb950" if stock['change_5d'] >= 0 else "#f85149"
    arrow = "▲" if stock['change_5d'] >= 0 else "▼"

    signals_html = ""
    for s in stock['signals']:
        signals_html += f"<div style='font-size:12px;color:#8b949e'>• {html.escape(s)}</div>"

    st.markdown(f"""
    <div style="background:#161b22;padding:12px;border-radius:10px;
    border:1px solid #30363d;margin-bottom:6px">
        <b style="font-size:1rem">{html.escape(stock['ticker'])}</b>
        <span style="float:right;color:#e6edf3">₹{stock['price']}</span>
        <div style="color:{color};margin-top:5px;font-weight:600">
            {arrow} {abs(stock['change_5d'])}%</div>
        <div style="margin-top:8px;font-size:12px;color:#8b949e">
            Signal {stock['signal_score']}/8</div>
        <div style="background:#21262d;height:6px;margin-top:3px;border-radius:4px">
            <div style="background:{color};width:{pct}%;height:6px;border-radius:4px"></div>
        </div>
        <div style="margin-top:6px">{signals_html}</div>
    </div>
    """, unsafe_allow_html=True)

    btn_key    = f"btn_{column_type}_{stock['ticker']}"
    result_key = f"ai_{column_type}_{stock['ticker']}"

    if st.button(f"🔍 Analyze {stock['ticker']}", key=btn_key, use_container_width=True):
        with st.spinner("AI analyzing..."):
            st.session_state[result_key] = get_ai(stock)

    if result_key in st.session_state and st.session_state[result_key]:
        render_ai_result(st.session_state[result_key])


# ---------------- MAIN ----------------
def show_radar():
    import datetime
    st.title("📡 Opportunity Radar")

    # ── Market status banner ──
    now = datetime.datetime.now(
        datetime.timezone(datetime.timedelta(hours=5, minutes=30))
    )
    market_open = now.weekday() < 5 and 9 <= now.hour < 16
    status = "🟢 Market Open — Live Data updating every 15 min" if market_open else "🔴 Market Closed — Showing Last Session Data (opens 9:15 AM IST)"
    color  = "#3fb950" if market_open else "#f85149"
    st.markdown(f"""
    <div style="background:#161b22;border:1px solid #30363d;
    border-left:3px solid {color};border-radius:8px;
    padding:10px 16px;margin-bottom:16px;font-size:0.85rem;color:{color}">
        {status} · Scanning top 20 NSE stocks by signal strength
    </div>
    """, unsafe_allow_html=True)

    if "radar_data" not in st.session_state:
        st.session_state.radar_data = None
    if "radar_scanned_at" not in st.session_state:
        st.session_state.radar_scanned_at = None

    if st.button("🔍 Scan Market", key="scan_market_main", use_container_width=True):
        results = []
        with st.spinner("Scanning NSE stocks..."):
            for t in NSE_STOCKS:
                d = fetch_stock_signals(t)
                if d and d['signal_score'] > 0:
                    results.append(d)
        results.sort(key=lambda x: x['signal_score'], reverse=True)
        st.session_state.radar_data = results
        st.session_state.radar_scanned_at = now.strftime("%d %b %Y, %I:%M %p IST")

    # ── Last scanned time ──
    if st.session_state.radar_scanned_at:
        st.caption(f"Last scanned: {st.session_state.radar_scanned_at}")

    if st.session_state.radar_data:
        data   = st.session_state.radar_data
        high   = [x for x in data if x['signal_score'] >= 5]
        medium = [x for x in data if 3 <= x['signal_score'] < 5]
        low    = [x for x in data if x['signal_score'] < 3]

        # ── Summary bar ──
        st.markdown(f"""
        <div style="background:#161b22;border:1px solid #30363d;
        border-radius:8px;padding:10px 16px;margin-bottom:12px;
        font-size:0.85rem;color:#8b949e">
            {len(data)} stocks with signals found —
            <span style="color:#f85149">{len(high)} High</span> ·
            <span style="color:#d29922">{len(medium)} Medium</span> ·
            <span style="color:#3fb950">{len(low)} Low</span>
        </div>
        """, unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        with c1:
            st.subheader("🔴 High Signals")
            if not high:
                st.write("No signals")
            for s in high:
                render_card(s, "high")
        with c2:
            st.subheader("🟡 Medium Signals")
            if not medium:
                st.write("No signals")
            for s in medium:
                render_card(s, "medium")
        with c3:
            st.subheader("🟢 Low Signals")
            if not low:
                st.write("No signals")
            for s in low:
                render_card(s, "low")