import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots

INDICES = {
    "NIFTY 50": "^NSEI",
    "SENSEX": "^BSESN",
    "NIFTY BANK": "^NSEBANK",
    "NIFTY IT": "^CNXIT"
}

def get_index_data(ticker):
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="7d")
        info = stock.fast_info
        price = round(info.last_price, 2)
        prev = round(info.previous_close, 2)
        change = round(price - prev, 2)
        pct = round((change / prev) * 100, 2)
        sparkline = hist['Close'].tolist()
        return {
            "price": price,
            "change": change,
            "pct": pct,
            "sparkline": sparkline
        }
    except:
        return None

def build_index_sparkline(prices, change):
    color = "#3fb950" if change >= 0 else "#f85149"
    fill_color = (
        "rgba(63,185,80,0.15)" if change >= 0
        else "rgba(248,81,73,0.15)"
    )
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        y=prices,
        mode='lines',
        line=dict(color=color, width=2),
        fill='tozeroy',
        fillcolor=fill_color,
        showlegend=False
    ))
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=0, b=0),
        height=55,
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
    )
    return fig

def build_market_heatmap(market_data):
    names = list(market_data.keys())
    pcts = [market_data[n]['pct'] for n in names]
    colors = ["#3fb950" if p >= 0 else "#f85149" for p in pcts]

    fig = go.Figure(go.Bar(
        x=names,
        y=[abs(p) for p in pcts],
        marker_color=colors,
        text=[f"{'+' if p >= 0 else ''}{p}%" for p in pcts],
        textposition='outside',
        textfont=dict(color='#e6edf3', size=13)
    ))
    fig.update_layout(
        paper_bgcolor='#0d1117',
        plot_bgcolor='#161b22',
        font=dict(color='#e6edf3'),
        xaxis=dict(gridcolor='#21262d'),
        yaxis=dict(gridcolor='#21262d', showticklabels=False),
        height=200,
        margin=dict(l=0, r=0, t=20, b=0),
        showlegend=False
    )
    return fig

def show_dashboard():
    st.markdown("# 📈 AI Investor Platform")
    st.markdown("*Your intelligent investment decision engine — ET AI Hackathon 2026*")
    st.divider()

    # ── Impact Metrics ──────────────────────────────────────────
    st.markdown("### In The Problem We Are Solving")
    m1, m2, m3, m4 = st.columns(4)

    metrics = [
        ("#58a6ff", "14Cr+", "Demat accounts in India",
         "Most investing blind"),
        ("#f85149", "95%", "Investors without a plan",
         "React to tips not data"),
        ("#d29922", "₹25K+", "Human advisor costs/year",
         "Only HNIs can afford"),
        ("#3fb950", "FREE", "Cost of our AI advisor",
         "Available to everyone"),
    ]

    for col, (color, number, label, sub) in zip(
        [m1, m2, m3, m4], metrics
    ):
        with col:
            st.markdown(f"""
            <div style="background:#161b22;border:1px solid #30363d;
            border-top:3px solid {color};border-radius:10px;
            padding:18px;text-align:center;min-height:120px">
                <div style="font-size:1.8rem;font-weight:700;
                color:{color};margin-bottom:4px">{number}</div>
                <div style="font-size:0.85rem;font-weight:600;
                color:#e6edf3;margin-bottom:4px">{label}</div>
                <div style="font-size:0.75rem;
                color:#8b949e">{sub}</div>
            </div>
            """, unsafe_allow_html=True)

    st.divider()

    # ── Live Market ─────────────────────────────────────────────
    st.markdown("### 🌍 Live Market Overview")

    market_data = {}
    cols = st.columns(4)
    for i, (name, ticker) in enumerate(INDICES.items()):
        with cols[i]:
            data = get_index_data(ticker)
            if data:
                market_data[name] = data
                color = "#3fb950" if data['change'] >= 0 else "#f85149"
                arrow = "▲" if data['change'] >= 0 else "▼"
                badge_bg = (
                    "rgba(63,185,80,0.15)" if data['change'] >= 0
                    else "rgba(248,81,73,0.15)"
                )
                st.markdown(f"""
                <div style="background:#161b22;border:1px solid #30363d;
                border-radius:10px;padding:14px;margin-bottom:4px">
                    <div style="font-size:0.78rem;color:#8b949e;
                    margin-bottom:4px">{name}</div>
                    <div style="font-size:1.35rem;font-weight:700;
                    color:#e6edf3;margin-bottom:6px">
                        {data['price']:,}
                    </div>
                    <div style="display:inline-block;
                    background:{badge_bg};color:{color};
                    padding:2px 10px;border-radius:20px;
                    font-size:0.85rem;font-weight:600">
                        {arrow} {abs(data['pct'])}%
                    </div>
                </div>
                """, unsafe_allow_html=True)

                if data['sparkline'] and len(data['sparkline']) > 2:
                    st.plotly_chart(
                        build_index_sparkline(
                            data['sparkline'], data['change']
                        ),
                        use_container_width=True,
                        key=f"spark_dash_{name}",
                        config={'displayModeBar': False}
                    )
            else:
                st.markdown(f"""
                <div style="background:#161b22;border:1px solid #30363d;
                border-radius:10px;padding:14px;text-align:center;
                color:#8b949e;font-size:0.85rem">
                    {name}<br>Loading...
                </div>
                """, unsafe_allow_html=True)

    # Market bar chart
    if market_data:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### Today's Performance")
        st.plotly_chart(
            build_market_heatmap(market_data),
            use_container_width=True,
            key="market_heatmap"
        )

    st.divider()

    # ── Features ────────────────────────────────────────────────
    st.markdown("### 🚀 Platform Features")

    f1, f2, f3, f4 = st.columns(4)
    features = [
        ("#58a6ff", "📂", "Portfolio Analyzer",
         "Upload CAMS statement",
         "Get XIRR, overlap detection, fund health score and AI recommendations instantly"),
        ("#d29922", "🔦", "Opportunity Radar",
         "NSE signal detection",
         "AI scans 20 stocks for volume spikes, momentum, and breakout patterns"),
        ("#a371f7", "📊", "Chart Intelligence",
         "Pattern detection",
         "RSI, Moving Average, Bollinger Bands explained in plain simple English"),
        ("#3fb950", "🎬", "Market Video Engine",
         "Auto-generated scripts",
         "AI writes broadcast-quality market update scripts from live data"),
    ]

    for col, (color, icon, title, subtitle, desc) in zip(
        [f1, f2, f3, f4], features
    ):
        with col:
            st.markdown(f"""
            <div style="background:#161b22;border:1px solid #30363d;
            border-top:3px solid {color};border-radius:10px;
            padding:16px;min-height:180px">
                <div style="font-size:1.6rem;margin-bottom:8px">
                    {icon}
                </div>
                <div style="font-size:0.9rem;font-weight:600;
                color:#e6edf3;margin-bottom:2px">{title}</div>
                <div style="font-size:0.75rem;color:{color};
                font-weight:600;margin-bottom:8px">{subtitle}</div>
                <div style="font-size:0.78rem;color:#8b949e;
                line-height:1.6">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    st.divider()

    # ── Agent Architecture ──────────────────────────────────────
    st.markdown("### 🤖 Multi-Agent Architecture")

    a1, a2, a3, a4, a5 = st.columns(5)
    agents = [
        ("#3fb950", "🧠", "Orchestrator", "Master agent — routes all requests"),
        ("#58a6ff", "📂", "Portfolio Agent", "Analyzes funds and generates advice"),
        ("#d29922", "🔦", "Radar Agent", "Scans NSE for market signals"),
        ("#a371f7", "📊", "Chart Agent", "Detects RSI and MA patterns"),
        ("#f85149", "🎬", "Video Agent", "Generates market video scripts"),
    ]

    for col, (color, icon, name, role) in zip(
        [a1, a2, a3, a4, a5], agents
    ):
        with col:
            st.markdown(f"""
            <div style="background:#161b22;border:1px solid #30363d;
            border-left:3px solid {color};border-radius:10px;
            padding:12px;text-align:center;min-height:130px">
                <div style="font-size:1.4rem;margin-bottom:6px">
                    {icon}
                </div>
                <div style="font-size:0.82rem;font-weight:600;
                color:{color};margin-bottom:4px">{name}</div>
                <div style="font-size:0.72rem;color:#8b949e;
                line-height:1.5">{role}</div>
            </div>
            """, unsafe_allow_html=True)

    st.divider()

    # ── Tech Stack ──────────────────────────────────────────────
    st.markdown("### ⚙️ Technology Stack")

    tech = [
        ("Groq LLM", "Llama 3.3 70B", "#58a6ff"),
        ("yfinance", "Live NSE data", "#3fb950"),
        ("MFAPI.in", "Mutual fund NAV", "#d29922"),
        ("Plotly", "Interactive charts", "#a371f7"),
        ("Streamlit", "Web interface", "#f85149"),
        ("pandas + ta", "Technical analysis", "#8b949e"),
    ]

    tcols = st.columns(6)
    for col, (name, desc, color) in zip(tcols, tech):
        with col:
            st.markdown(f"""
            <div style="background:#161b22;border:1px solid #30363d;
            border-radius:8px;padding:10px;text-align:center">
                <div style="font-size:0.82rem;font-weight:600;
                color:{color};margin-bottom:2px">{name}</div>
                <div style="font-size:0.72rem;
                color:#8b949e">{desc}</div>
            </div>
            """, unsafe_allow_html=True)