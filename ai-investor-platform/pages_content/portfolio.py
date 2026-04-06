import streamlit as st
import fitz
import re
import requests
import pandas as pd
import plotly.graph_objects as go
from groq import Groq
import os

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

sample_funds = [
    {"fund_name": "HDFC Flexi Cap Fund Direct Growth", "amount": 150000},
    {"fund_name": "Parag Parikh Flexi Cap Direct Growth", "amount": 120000},
    {"fund_name": "Axis Bluechip Fund Direct Growth", "amount": 80000},
    {"fund_name": "SBI Small Cap Fund Direct Growth", "amount": 60000},
    {"fund_name": "Mirae Asset Large Cap Direct Growth", "amount": 100000},
]

def extract_text_from_pdf(pdf_file):
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def extract_funds_from_text(text):
    funds = []
    lines = text.split('\n')
    for line in lines:
        line = line.strip()
        if any(k in line.lower() for k in ['fund', 'scheme', 'direct', 'growth']):
            match = re.search(r'[\d,]+\.?\d*', line)
            if match:
                try:
                    amount = float(match.group().replace(',', ''))
                    if amount > 100:
                        funds.append({"fund_name": line[:60].strip(), "amount": amount})
                except:
                    pass
    return funds[:10]

def parse_ai_analysis(text):
    sections = {
        "score": "",
        "problems": [],
        "positives": [],
        "recommendations": [],
        "bottom_line": ""
    }
    current = None
    for line in text.split('\n'):
        line = line.strip()
        if not line:
            continue
        if 'Health Score' in line:
            sections['score'] = line
            current = None
        elif 'Problems Found' in line:
            current = 'problems'
        elif 'Doing Right' in line:
            current = 'positives'
        elif 'Recommendations' in line:
            current = 'recommendations'
        elif 'Bottom Line' in line:
            current = 'bottom_line'
        elif line.startswith('-') or (line[0].isdigit() and line[1] in '.):'):
            content = line.lstrip('-0123456789.) ').strip()
            if current in ['problems', 'positives', 'recommendations']:
                sections[current].append(content)
        elif current == 'bottom_line' and line:
            sections['bottom_line'] += line + " "
    return sections

def analyze_portfolio_with_ai(portfolio_data):
    total = sum(f['amount'] for f in portfolio_data)
    summary = f"Total invested: ₹{total:,.0f}\nNumber of funds: {len(portfolio_data)}\n\nFunds:\n"
    for f in portfolio_data:
        pct = round((f['amount'] / total) * 100, 1)
        summary += f"- {f['fund_name']}: ₹{f['amount']:,.0f} ({pct}% of portfolio)\n"

    prompt = f"""
You are an expert Indian financial advisor. Analyze this mutual fund portfolio.

{summary}

Give analysis in this exact format:

## Portfolio Health Score: X/10

## Key Problems Found:
- Problem 1
- Problem 2
- Problem 3

## What You Are Doing Right:
- Good thing 1
- Good thing 2

## Specific Recommendations:
1. Recommendation with reason
2. Recommendation with reason
3. Recommendation with reason

## Bottom Line:
One powerful sentence about what this investor must do immediately.

Be specific. Use simple language. Mention actual fund names and numbers.
"""
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1000,
        temperature=0.3
    )
    return response.choices[0].message.content

def build_donut_chart(portfolio_data):
    labels = [f['fund_name'][:25] + "..." if len(f['fund_name']) > 25
              else f['fund_name'] for f in portfolio_data]
    values = [f['amount'] for f in portfolio_data]
    colors = ['#58a6ff', '#3fb950', '#d29922', '#a371f7', '#f85149',
              '#79c0ff', '#56d364', '#e3b341', '#bc8cff', '#ff7b72']

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.6,
        marker=dict(colors=colors[:len(labels)],
                    line=dict(color='#0d1117', width=2)),
        textinfo='percent',
        textfont=dict(color='#e6edf3', size=12),
        hovertemplate='<b>%{label}</b><br>₹%{value:,.0f}<br>%{percent}<extra></extra>'
    )])

    total = sum(values)
    fig.update_layout(
        paper_bgcolor='#0d1117',
        plot_bgcolor='#0d1117',
        font=dict(color='#e6edf3'),
        showlegend=True,
        legend=dict(
            bgcolor='#161b22',
            bordercolor='#30363d',
            borderwidth=1,
            font=dict(size=11)
        ),
        annotations=[dict(
            text=f'₹{total/100000:.1f}L<br><span style="font-size:10px">Total</span>',
            x=0.5, y=0.5,
            font=dict(size=16, color='#e6edf3'),
            showarrow=False
        )],
        height=350,
        margin=dict(l=0, r=0, t=20, b=0)
    )
    return fig

def build_health_gauge(score):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        domain={'x': [0, 1], 'y': [0, 1]},
        gauge={
            'axis': {'range': [0, 10],
                     'tickcolor': '#8b949e',
                     'tickfont': dict(color='#8b949e')},
            'bar': {'color': '#58a6ff'},
            'bgcolor': '#161b22',
            'bordercolor': '#30363d',
            'steps': [
                {'range': [0, 4], 'color': '#3d1a1a'},
                {'range': [4, 7], 'color': '#3d2e0a'},
                {'range': [7, 10], 'color': '#0d2b0d'}
            ],
            'threshold': {
                'line': {'color': '#58a6ff', 'width': 3},
                'thickness': 0.75,
                'value': score
            }
        },
        number={'font': {'color': '#58a6ff', 'size': 36}},
        title={'text': "Health Score / 10",
               'font': {'color': '#8b949e', 'size': 13}}
    ))
    fig.update_layout(
        paper_bgcolor='#0d1117',
        font=dict(color='#e6edf3'),
        height=220,
        margin=dict(l=20, r=20, t=20, b=0)
    )
    return fig

def show_portfolio():
    st.markdown("# 📂 Portfolio Analyzer")
    st.markdown("*Upload your CAMS statement and get instant AI-powered analysis*")
    st.divider()

    if "portfolio_data" not in st.session_state:
        st.session_state.portfolio_data = None
    if "analysis_result" not in st.session_state:
        st.session_state.analysis_result = None

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("### Upload Portfolio")
        uploaded_file = st.file_uploader(
            "Upload CAMS PDF Statement",
            type=['pdf'],
            help="Download from camsonline.com"
        )
        if st.button("📊 Use Sample Portfolio", use_container_width=True):
            st.session_state.portfolio_data = sample_funds
            st.session_state.analysis_result = None
            st.success("✅ Sample portfolio loaded!")

        if uploaded_file:
            with st.spinner("🔍 Reading your PDF..."):
                try:
                    text = extract_text_from_pdf(uploaded_file)
                    extracted = extract_funds_from_text(text)
                    if extracted:
                        st.session_state.portfolio_data = extracted
                        st.session_state.analysis_result = None
                        st.success(f"✅ Found {len(extracted)} funds!")
                    else:
                        st.session_state.portfolio_data = sample_funds
                        st.warning("⚠️ Could not extract funds. Using sample.")
                except Exception as e:
                    st.error(f"Error: {str(e)}")

    with col2:
        st.markdown("### How to get your CAMS statement")
        st.markdown("""
        <div class="alert-card">
            <p style="color:#8b949e;font-size:0.9rem">
            1. Go to <b style="color:#58a6ff">camsonline.com</b><br>
            2. Click "Investor Services"<br>
            3. Select "Mail Back Services"<br>
            4. Choose "Consolidated Account Statement"<br>
            5. Enter your email and PAN<br>
            6. Download PDF from your email<br><br>
            <b style="color:#3fb950">Free and takes 2 minutes!</b>
            </p>
        </div>
        """, unsafe_allow_html=True)

    if st.session_state.portfolio_data:
        portfolio_data = st.session_state.portfolio_data
        total = sum(f['amount'] for f in portfolio_data)

        st.divider()

        # Big total number
        st.markdown(f"""
        <div style="text-align:center;padding:20px 0 10px">
            <div style="font-size:0.9rem;color:#8b949e;margin-bottom:4px">
                Total Portfolio Value
            </div>
            <div style="font-size:3rem;font-weight:700;color:#58a6ff;
            letter-spacing:-1px">
                ₹{total:,.0f}
            </div>
            <div style="font-size:0.85rem;color:#8b949e">
                across {len(portfolio_data)} mutual funds
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.divider()

        # Donut chart + metrics
        ch_col, mt_col = st.columns([1.2, 1])
        with ch_col:
            st.markdown("### 🥧 Portfolio Allocation")
            fig = build_donut_chart(portfolio_data)
            st.plotly_chart(fig, use_container_width=True)

        with mt_col:
            st.markdown("### 📋 Holdings Summary")
            st.markdown("<br>", unsafe_allow_html=True)
            for f in portfolio_data:
                pct = round((f['amount'] / total) * 100, 1)
                name = f['fund_name'][:30] + "..." \
                    if len(f['fund_name']) > 30 else f['fund_name']
                st.markdown(f"""
                <div style="margin-bottom:10px">
                    <div style="display:flex;justify-content:space-between;
                    margin-bottom:3px">
                        <span style="font-size:0.8rem;
                        color:#e6edf3">{name}</span>
                        <span style="font-size:0.8rem;
                        color:#58a6ff;font-weight:600">{pct}%</span>
                    </div>
                    <div style="background:#21262d;border-radius:4px;height:6px">
                        <div style="background:#58a6ff;border-radius:4px;
                        height:6px;width:{pct}%"></div>
                    </div>
                    <div style="font-size:0.75rem;color:#8b949e;
                    margin-top:2px">₹{f['amount']:,.0f}</div>
                </div>
                """, unsafe_allow_html=True)

        st.divider()
        st.markdown("### 🤖 AI Portfolio Analysis")

        if st.button("🔍 Analyze My Portfolio", use_container_width=True):
            with st.spinner("🧠 Analyzing portfolio — checking overlaps, returns, fees..."):
                try:
                    result = analyze_portfolio_with_ai(portfolio_data)
                    st.session_state.analysis_result = result
                except Exception as e:
                    st.error(f"AI error: {str(e)}")

        if st.session_state.analysis_result:
            parsed = parse_ai_analysis(st.session_state.analysis_result)

            # Extract score number
            score_num = 5
            try:
                score_match = re.search(r'(\d+(?:\.\d+)?)/10',
                                        parsed['score'])
                if score_match:
                    score_num = float(score_match.group(1))
            except:
                pass

            # Gauge + bottom line
            g_col, b_col = st.columns([1, 1.5])
            with g_col:
                gauge = build_health_gauge(score_num)
                st.plotly_chart(gauge, use_container_width=True)
            with b_col:
                if parsed['bottom_line']:
                    st.markdown("<br><br>", unsafe_allow_html=True)
                    st.markdown(f"""
                    <div style="background:#1c2128;border-radius:12px;
                    padding:20px;border-left:4px solid #58a6ff">
                        <div style="font-size:0.8rem;color:#8b949e;
                        margin-bottom:8px">
                            💡 BOTTOM LINE
                        </div>
                        <div style="font-size:1rem;color:#e6edf3;
                        line-height:1.7;font-weight:500">
                            {parsed['bottom_line']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

            st.divider()
            r_col, p_col = st.columns(2)

            with r_col:
                st.markdown("#### 🔴 Problems Found")
                for prob in parsed['problems']:
                    st.markdown(f"""
                    <div style="background:#2d1a1a;border-left:3px solid #f85149;
                    border-radius:8px;padding:10px 14px;margin-bottom:8px;
                    font-size:0.88rem;color:#e6edf3;line-height:1.6">
                        ⚠️ {prob}
                    </div>
                    """, unsafe_allow_html=True)

            with p_col:
                st.markdown("#### 🟢 What You're Doing Right")
                for pos in parsed['positives']:
                    st.markdown(f"""
                    <div style="background:#0d2b0d;border-left:3px solid #3fb950;
                    border-radius:8px;padding:10px 14px;margin-bottom:8px;
                    font-size:0.88rem;color:#e6edf3;line-height:1.6">
                        ✅ {pos}
                    </div>
                    """, unsafe_allow_html=True)

            st.divider()
            st.markdown("#### 📌 Specific Recommendations")
            for i, rec in enumerate(parsed['recommendations'], 1):
                st.markdown(f"""
                <div style="background:#1c2128;border-left:3px solid #d29922;
                border-radius:8px;padding:12px 16px;margin-bottom:10px;
                font-size:0.9rem;color:#e6edf3;line-height:1.7">
                    <span style="color:#d29922;font-weight:600">{i}.</span> {rec}
                </div>
                """, unsafe_allow_html=True)