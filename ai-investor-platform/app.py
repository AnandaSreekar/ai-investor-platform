import streamlit as st

st.set_page_config(
    page_title="AI Investor Platform",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Base ── */
html, body, [data-testid="stAppViewContainer"] {
    background: #0A0E1A !important;
}
[data-testid="stSidebar"] {
    background: #0F1629 !important;
    border-right: 1px solid #1E2A45 !important;
}
[data-testid="stSidebar"] > div:first-child {
    padding-top: 0 !important;
}

/* ── Sidebar header band ── */
.sidebar-header {
    background: linear-gradient(135deg, #00D4AA15, #3B82F615);
    border-bottom: 1px solid #1E2A45;
    padding: 20px 16px 16px;
    margin-bottom: 8px;
}
.sidebar-logo {
    font-size: 1.4rem;
    font-weight: 800;
    color: #E2E8F0;
    letter-spacing: -0.5px;
}
.sidebar-logo span { color: #00D4AA; }
.sidebar-sub {
    font-size: 0.7rem;
    color: #64748B;
    margin-top: 2px;
    letter-spacing: 0.5px;
    text-transform: uppercase;
}

/* ── Live badge ── */
.live-badge {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    background: #00D4AA15;
    border: 1px solid #00D4AA40;
    border-radius: 20px;
    padding: 3px 10px;
    font-size: 0.68rem;
    color: #00D4AA;
    font-weight: 600;
    margin-top: 8px;
}
.live-dot {
    width: 6px; height: 6px;
    background: #00D4AA;
    border-radius: 50%;
    animation: pulse 1.5s infinite;
}
@keyframes pulse {
    0%,100% { opacity:1; }
    50%      { opacity:0.3; }
}

/* ── Nav section label ── */
.nav-label {
    font-size: 0.62rem;
    color: #475569;
    font-weight: 700;
    letter-spacing: 1.2px;
    text-transform: uppercase;
    padding: 12px 16px 4px;
}

/* ── Nav buttons ── */
div[data-testid="stRadio"] > div {
    gap: 2px !important;
}
div[data-testid="stRadio"] label {
    background: transparent !important;
    border-radius: 8px !important;
    padding: 8px 12px !important;
    cursor: pointer !important;
    transition: all 0.15s !important;
    border: 1px solid transparent !important;
    width: 100% !important;
}
div[data-testid="stRadio"] label:hover {
    background: #1E2A4520 !important;
    border-color: #1E2A45 !important;
}
div[data-testid="stRadio"] label[data-checked="true"] {
    background: #00D4AA15 !important;
    border-color: #00D4AA40 !important;
}

/* ── Sidebar footer ── */
.sidebar-footer {
    border-top: 1px solid #1E2A45;
    padding: 12px 16px;
    margin-top: 16px;
}
.powered-tag {
    font-size: 0.65rem;
    color: #475569;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin-bottom: 6px;
}
.tech-chips {
    display: flex;
    flex-wrap: wrap;
    gap: 4px;
    margin-top: 4px;
}
.chip {
    background: #1E2A45;
    border: 1px solid #2D3F5E;
    border-radius: 4px;
    padding: 2px 7px;
    font-size: 0.65rem;
    color: #94A3B8;
}

/* ── Top header bar ── */
.topbar {
    background: linear-gradient(90deg, #0F1629, #0A0E1A);
    border-bottom: 1px solid #1E2A45;
    padding: 10px 0 12px;
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.topbar-title {
    font-size: 0.75rem;
    color: #475569;
    text-transform: uppercase;
    letter-spacing: 1px;
}
.topbar-right {
    font-size: 0.72rem;
    color: #00D4AA;
}

/* ── Streamlit overrides ── */
.stButton > button {
    background: linear-gradient(135deg, #00D4AA, #0EA5E9) !important;
    color: #0A0E1A !important;
    font-weight: 700 !important;
    border: none !important;
    border-radius: 8px !important;
    transition: opacity 0.2s !important;
}
.stButton > button:hover {
    opacity: 0.88 !important;
}
h1, h2, h3 {
    color: #E2E8F0 !important;
}
.stSpinner > div {
    border-top-color: #00D4AA !important;
}
[data-testid="stMetricValue"] {
    color: #00D4AA !important;
}
hr {
    border-color: #1E2A45 !important;
}
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:

    # Logo + header
    st.markdown("""
    <div class="sidebar-header">
        <div class="sidebar-logo">📈 <span>AI</span>nvestor</div>
        <div class="sidebar-sub">ET AI Hackathon 2026</div>
        <div class="live-badge">
            <div class="live-dot"></div> NSE Live Data
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Nav label
    st.markdown('<div class="nav-label">Navigation</div>', unsafe_allow_html=True)

    # Navigation
    pages = [
        "🌐  Market Overview",
        "💼  Portfolio Insights",
        "🎯  Trade Opportunities",
        "🔬  Stock Deep Dive",
        "📺  Market Briefings",
    ]
    page = st.radio("", pages, label_visibility="collapsed")

    # Footer
    st.markdown("""
    <div class="sidebar-footer">
        <div class="powered-tag">Powered by</div>
        <div class="tech-chips">
            <span class="chip">Groq LLM</span>
            <span class="chip">yfinance</span>
            <span class="chip">Plotly</span>
            <span class="chip">Streamlit</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── Page routing ──────────────────────────────────────────────────────────────
if page == "🌐  Market Overview":
    from pages_content.dashboard import show_dashboard
    show_dashboard()

elif page == "💼  Portfolio Insights":
    from pages_content.portfolio import show_portfolio
    show_portfolio()

elif page == "🎯  Trade Opportunities":
    from pages_content.radar import show_radar
    show_radar()

elif page == "🔬  Stock Deep Dive":
    from pages_content.chart import show_chart
    show_chart()

elif page == "📺  Market Briefings":
    from pages_content.video_preview import show_video
    show_video()