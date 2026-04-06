import streamlit as st
import fitz
import re
import requests
import pandas as pd
import plotly.graph_objects as go
from groq import Groq
import os
import random

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ---------------- SAMPLE DATA ----------------
sample_funds = [
    {"fund_name": "HDFC Flexi Cap Fund Direct Growth", "amount": 150000},
    {"fund_name": "Parag Parikh Flexi Cap Direct Growth", "amount": 120000},
    {"fund_name": "Axis Bluechip Fund Direct Growth", "amount": 80000},
    {"fund_name": "SBI Small Cap Fund Direct Growth", "amount": 60000},
    {"fund_name": "Mirae Asset Large Cap Direct Growth", "amount": 100000},
]

# ---------------- SIMULATION ----------------
def simulate_current_value(amount):
    change_pct = random.uniform(-0.08, 0.12)
    current = amount * (1 + change_pct)
    pnl = current - amount
    pnl_pct = (pnl / amount) * 100
    return current, pnl, pnl_pct

# ---------------- PDF EXTRACTION ----------------
def extract_text_from_pdf(pdf_file):
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def extract_funds_from_text(text):
    funds = []
    for line in text.split('\n'):
        if any(k in line.lower() for k in ['fund', 'scheme', 'direct']):
            match = re.search(r'[\d,]+\.?\d*', line)
            if match:
                try:
                    amount = float(match.group().replace(',', ''))
                    if amount > 100:
                        funds.append({"fund_name": line[:60], "amount": amount})
                except:
                    pass
    return funds[:10]

# ---------------- DONUT ----------------
def build_donut_chart(portfolio_data):
    labels = [f['fund_name'][:25] + "..." for f in portfolio_data]
    values = [f['amount'] for f in portfolio_data]

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.6,
        textinfo='percent',
        marker=dict(line=dict(color='#0d1117', width=2))
    )])

    total = sum(values)
    fig.update_layout(
        paper_bgcolor='#0d1117',
        font=dict(color='#e6edf3'),
        annotations=[dict(
            text=f'₹{total/100000:.1f}L<br>Total',
            x=0.5, y=0.5,
            showarrow=False
        )]
    )
    return fig

# ---------------- MAIN ----------------
def show_portfolio():
    st.markdown("# 📂 Portfolio Analyzer")
    st.divider()

    if "portfolio_data" not in st.session_state:
        st.session_state.portfolio_data = None

    col1, col2 = st.columns(2)

    with col1:
        uploaded_file = st.file_uploader("Upload CAMS PDF", type=['pdf'])

        if st.button("Use Sample"):
            st.session_state.portfolio_data = sample_funds

        if uploaded_file:
            text = extract_text_from_pdf(uploaded_file)
            data = extract_funds_from_text(text)
            st.session_state.portfolio_data = data if data else sample_funds

    with col2:
        st.info("Upload CAMS or use sample portfolio")

    if st.session_state.portfolio_data:
        data = st.session_state.portfolio_data
        total = sum(f['amount'] for f in data)

        st.markdown(f"## ₹{total:,.0f}")

        # -------- CHART + HOLDINGS --------
        ch_col, mt_col = st.columns([1.2, 1])

        with ch_col:
            st.subheader("Portfolio Allocation")
            fig = build_donut_chart(data)
            st.plotly_chart(fig, use_container_width=True)

        with mt_col:
            st.subheader("Holdings Summary")

            for f in data:
                current, pnl, pnl_pct = simulate_current_value(f['amount'])
                color = "#3fb950" if pnl >= 0 else "#f85149"

                st.markdown(f"""
                <div style="background:#161b22;padding:12px;border-radius:10px;
                margin-bottom:10px;border-left:4px solid {color}">

                    <div style="font-weight:600;color:#58a6ff">
                        {f['fund_name'][:35]}
                    </div>

                    <div style="font-size:0.8rem;color:#8b949e">
                        Invested: ₹{f['amount']:,.0f}
                    </div>

                    <div style="font-size:0.8rem;color:#8b949e">
                        Current: ₹{current:,.0f}
                    </div>

                    <div style="color:{color};font-weight:600">
                        {'▲' if pnl>=0 else '▼'} ₹{pnl:,.0f} ({pnl_pct:.2f}%)
                    </div>

                </div>
                """, unsafe_allow_html=True)

        st.divider()

        # -------- FUND DETAILS --------
        st.subheader("Detailed Insights")

        for f in data:
            current, pnl, pnl_pct = simulate_current_value(f['amount'])

            if pnl > 0:
                suggestion = "Strong performance — holding is fine"
                color = "#3fb950"
            else:
                suggestion = "Weak performance — review needed"
                color = "#f85149"

            st.markdown(f"""
            <div style="background:#1c2128;padding:12px;border-radius:8px;margin-bottom:8px">

                <div style="color:#58a6ff;font-weight:600">
                    {f['fund_name']}
                </div>

                <div style="font-size:0.8rem;color:#8b949e">
                    Current: ₹{current:,.0f}
                </div>

                <div style="color:{color}">
                    P&L: ₹{pnl:,.0f} ({pnl_pct:.2f}%)
                </div>

                <div style="font-size:0.8rem;color:#e6edf3">
                    💡 {suggestion}
                </div>

            </div>
            """, unsafe_allow_html=True)