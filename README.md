# 📈 AI Investor Platform
### ET AI Hackathon 2026 — Problem Statement 6: AI for the Indian Investor

> **Turning raw market data into actionable, money-making decisions for India's 14 crore+ retail investors.**

---

## 🧩 Problem We Solved

India has 14 crore+ demat accounts — but most retail investors are flying blind. They react to tips, miss filings, can't read technicals, and manage portfolios on gut feel.

**We built the intelligence layer that turns ET Markets data into decisions.**

---

## 🚀 Live Features Built

### 1. 🌐 Market Overview
- Live NIFTY 50, SENSEX, BANK NIFTY, NIFTY IT indices
- Sector heatmap with real-time % change
- Top gainers & losers of the day
- FII/DII activity tracker
- AI-generated market summary in plain English

### 2. 💼 Portfolio Insights
- Add stocks manually and track live P&L
- Portfolio allocation pie chart
- Sector-wise diversification analysis
- AI portfolio health score with recommendations
- Risk assessment per holding

### 3. 🎯 Trade Opportunities — Opportunity Radar
- Scans 20 NSE stocks for live signals
- Detects: volume spikes, momentum, breakouts, sharp drops
- Signal scoring system (out of 8)
- Three-tier signal board: High / Medium / Low
- Per-stock AI analysis with:
  - 🟢 BUY / 🔴 SELL / 🟡 HOLD recommendation
  - Confidence % bar
  - Risk level badge (LOW / MEDIUM / HIGH)
  - Plain-English tip for beginners

### 4. 🔬 Stock Deep Dive — Chart Pattern Intelligence
- Interactive Plotly candlestick chart
- Volume bars with color coding
- RSI (Relative Strength Index) indicator
- Support & resistance level detection
- Breakout, reversal, divergence pattern detection
- AI explanation of detected patterns in plain English
- Historical back-tested context

### 5. 📺 Market Briefings — AI Market Video Engine
- Fetches live NIFTY / SENSEX / BANK NIFTY data
- AI generates broadcast-quality 60-second TV anchor script
- Script segments: Intro → Market Summary → Key Highlight → What to Watch → Outro
- **Animated Sector Race Chart GIF** (auto-generated from live data)
- **Animated Index Sparklines GIF** (simulated intraday movement)
- Download script as `.txt`
- Download both GIFs
- v2.0 Roadmap: ElevenLabs voiceover + MoviePy MP4 rendering pipeline

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Streamlit |
| Charts | Plotly, Matplotlib |
| Market Data | yfinance |
| Technical Indicators | ta (Technical Analysis library) |
| AI / LLM | Groq API — LLaMA 3.3 70B |
| Animation | Matplotlib FuncAnimation + PillowWriter |
| Language | Python 3.11 |

---

## 📁 Project Structure

```
ai-investor-platform/
│
├── app.py                        # Main app — routing + UI shell
├── requirements.txt
├── .env                          # GROQ_API_KEY (not pushed)
├── .gitignore
│
├── .streamlit/
│   └── config.toml               # Theme — deep navy + teal fintech style
│
├── pages_content/
│   ├── dashboard.py              # Market Overview
│   ├── portfolio.py              # Portfolio Insights
│   ├── radar.py                  # Trade Opportunities / Opportunity Radar
│   ├── chart.py                  # Stock Deep Dive / Chart Intelligence
│   └── video_preview.py          # Market Briefings / AI Video Engine
│
├── agents/
│   ├── radar_agent.py            # Signal detection logic
│   ├── chart_agent.py            # Pattern detection logic
│   ├── portfolio_agent.py        # Portfolio analysis logic
│   └── orchestrator.py           # Agent coordination
│
└── utils/
    └── helpers.py                # Shared utilities
```

---

## ⚙️ Setup & Run

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/ai-investor-platform.git
cd ai-investor-platform
```

### 2. Create virtual environment
```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # Mac/Linux
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Add your Groq API key
Create a `.env` file in the root:
```
GROQ_API_KEY=your_groq_api_key_here
```
Get your free key at: https://console.groq.com

### 5. Run the app
```bash
streamlit run app.py
```

---

## 🔑 Environment Variables

| Variable | Description |
|---|---|
| `GROQ_API_KEY` | Groq LLM API key for AI analysis |

---

## 📊 What Makes This Different

| Feature | Traditional Apps | Our Platform |
|---|---|---|
| Signal Detection | Manual screening | AI-powered auto-scan |
| Chart Analysis | Raw charts only | Plain-English AI explanation |
| Portfolio | Just tracking | AI health score + advice |
| Market Updates | Text articles | Auto-generated animated video |
| Target User | Expert traders | Any retail investor |

---

## 🗺️ Roadmap — v2.0

- [ ] ElevenLabs voiceover integration
- [ ] MoviePy full MP4 video rendering
- [ ] NSE bulk/block deals filings monitor
- [ ] Insider trading alert system
- [ ] IPO tracker
- [ ] WhatsApp/Telegram alert bot
- [ ] Multi-stock portfolio optimizer

---

## 👨‍💻 Built For

**ET AI Hackathon 2026** — Problem Statement 6  
*"AI for the Indian Investor"*  
Build the intelligence layer that turns ET Markets data into actionable decisions.

---

## ⚠️ Disclaimer

This platform is built for educational and hackathon demonstration purposes only.  
It does not constitute financial advice. Always consult a SEBI-registered advisor before investing.
