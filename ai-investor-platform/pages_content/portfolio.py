import streamlit as st
import fitz
import re
import plotly.graph_objects as go
import random

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

# ---------------- PDF ----------------
def extract_text_from_pdf(pdf_file):
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def extract_funds_from_text(text):
    funds = []
    for line in text.split('\n'):
        if "fund" in line.lower():
            match = re.search(r'[\d,]+\.?\d*', line)
            if match:
                amount = float(match.group().replace(',', ''))
                funds.append({"fund_name": line[:60], "amount": amount})
    return funds[:10]

# ---------------- CHART ----------------
def build_donut_chart(data):
    labels = [f['fund_name'][:25] for f in data]
    values = [f['amount'] for f in data]

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.6,
        textinfo='percent'
    )])

    total = sum(values)

    fig.update_layout(
        paper_bgcolor='#0d1117',
        font=dict(color='white'),
        annotations=[dict(
            text=f"₹{total/100000:.1f}L<br>Total",
            x=0.5, y=0.5,
            showarrow=False
        )]
    )
    return fig

# ---------------- MAIN ----------------
def show_portfolio():

    st.markdown("# 📂 Portfolio Analyzer")
    st.markdown("*Upload your CAMS statement and get insights*")
    st.divider()

    if "portfolio_data" not in st.session_state:
        st.session_state.portfolio_data = None

    # -------- UPLOAD SECTION (RESTORED) --------
    col1, col2 = st.columns(2)

    with col1:
        uploaded_file = st.file_uploader("Upload CAMS PDF", type=['pdf'])

        if st.button("📊 Use Sample Portfolio"):
            st.session_state.portfolio_data = sample_funds
            st.success("Sample loaded")

        if uploaded_file:
            text = extract_text_from_pdf(uploaded_file)
            data = extract_funds_from_text(text)
            st.session_state.portfolio_data = data if data else sample_funds

    with col2:
        st.info("""
        How to get CAMS:
        1. Go to camsonline.com  
        2. Download CAS  
        3. Upload here  
        """)

    # -------- DISPLAY --------
    if st.session_state.portfolio_data:

        data = st.session_state.portfolio_data
        total = sum(f['amount'] for f in data)

        st.divider()

        st.markdown(f"## ₹{total:,.0f}")

        ch_col, mt_col = st.columns([1.2, 1])

        # -------- CHART --------
        with ch_col:
            st.subheader("Portfolio Allocation")
            fig = build_donut_chart(data)
            st.plotly_chart(fig, use_container_width=True)

        # -------- HOLDINGS (FIXED UI) --------
        with mt_col:
            st.subheader("Holdings Summary")

            for f in data:
                current, pnl, pnl_pct = simulate_current_value(f['amount'])
                color = "green" if pnl >= 0 else "red"

                st.markdown(
                    f"""
                    **{f['fund_name'][:35]}**

                    Invested: ₹{f['amount']:,.0f}  
                    Current: ₹{current:,.0f}  
                    <span style='color:{color}'>
                    {'▲' if pnl>=0 else '▼'} ₹{pnl:,.0f} ({pnl_pct:.2f}%)
                    </span>
                    """,
                    unsafe_allow_html=True
                )
                st.markdown("---")

        # -------- DETAILS --------
        st.divider()
        st.subheader("Detailed Insights")

        for f in data:
            current, pnl, pnl_pct = simulate_current_value(f['amount'])

            suggestion = (
                "Good performance — hold"
                if pnl > 0 else
                "Underperforming — review"
            )

            st.markdown(
                f"""
                **{f['fund_name']}**

                Current: ₹{current:,.0f}  
                P&L: ₹{pnl:,.0f} ({pnl_pct:.2f}%)  
                💡 {suggestion}
                """
            )
            st.markdown("---")