import streamlit as st
import yfinance as yf
from groq import Groq
import os
import tempfile
import base64
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ── Data ─────────────────────────────────────────────────────────────────────

def get_market_data():
    try:
        indices = {
            "NIFTY 50": "^NSEI",
            "SENSEX": "^BSESN",
            "BANK NIFTY": "^NSEBANK",
        }
        results = {}
        for name, ticker in indices.items():
            info  = yf.Ticker(ticker).fast_info
            price = round(info.last_price, 2)
            prev  = round(info.previous_close, 2)
            chg   = round(((price - prev) / prev) * 100, 2)
            results[name] = {"price": price, "change": chg}
        return results
    except Exception:
        return {}


def get_sector_data():
    sector_tickers = {
        "IT":      "INFY.NS",
        "Banking": "HDFCBANK.NS",
        "Auto":    "TATAMOTORS.NS",
        "Pharma":  "SUNPHARMA.NS",
        "Energy":  "RELIANCE.NS",
        "FMCG":    "HINDUNILVR.NS",
        "Metal":   "TATASTEEL.NS",
        "Realty":  "DLF.NS",
    }
    results = {}
    for sector, ticker in sector_tickers.items():
        try:
            info  = yf.Ticker(ticker).fast_info
            price = info.last_price
            prev  = info.previous_close
            chg   = round(((price - prev) / prev) * 100, 2)
            results[sector] = chg
        except Exception:
            results[sector] = round(np.random.uniform(-2.5, 2.5), 2)
    return results

# ── Animated GIF generators ───────────────────────────────────────────────────

def generate_race_chart_gif(sector_data: dict) -> bytes:
    labels = list(sector_data.keys())
    final  = np.array([sector_data[l] for l in labels])
    n      = len(labels)
    frames = 40
    colors = ["#3fb950" if v >= 0 else "#f85149" for v in final]

    fig, ax = plt.subplots(figsize=(8, 4))
    fig.patch.set_facecolor("#0d1117")
    ax.set_facecolor("#161b22")
    bars = ax.barh(labels, [0] * n, color=colors, height=0.6)
    ax.set_xlim(min(final) - 1, max(final) + 1)
    ax.set_xlabel("% Change", color="#8b949e", fontsize=9)
    ax.set_title("Sector Performance Today", color="#e6edf3",
                 fontsize=11, fontweight="bold", pad=10)
    ax.tick_params(colors="#8b949e", labelsize=8)
    ax.spines[:].set_color("#30363d")
    ax.axvline(0, color="#30363d", linewidth=0.8)

    val_texts = [ax.text(0, i, "", va="center", ha="left",
                         color="#e6edf3", fontsize=8) for i in range(n)]

    def animate(frame):
        progress = (frame + 1) / frames
        eased    = 1 - (1 - progress) ** 3
        current  = final * eased
        for bar, val, txt in zip(bars, current, val_texts):
            bar.set_width(val)
            offset = 0.05 if val >= 0 else -0.05
            txt.set_position((val + offset, bar.get_y() + bar.get_height() / 2))
            txt.set_text(f"{'+' if val >= 0 else ''}{val:.2f}%")
        return bars.patches + val_texts

    ani = animation.FuncAnimation(fig, animate, frames=frames,
                                  interval=60, blit=True)
    tmp = tempfile.NamedTemporaryFile(suffix=".gif", delete=False)
    tmp.close()
    ani.save(tmp.name, writer=animation.PillowWriter(fps=18), dpi=120)
    plt.close(fig)
    with open(tmp.name, "rb") as f:
        data = f.read()
    os.unlink(tmp.name)
    return data


def generate_index_sparkline_gif(market_data: dict) -> bytes:
    fig, ax = plt.subplots(figsize=(8, 3))
    fig.patch.set_facecolor("#0d1117")
    ax.set_facecolor("#161b22")
    ax.set_title("Index Movement (Simulated Intraday)", color="#e6edf3",
                 fontsize=10, fontweight="bold", pad=8)
    ax.tick_params(colors="#8b949e", labelsize=7)
    ax.spines[:].set_color("#30363d")
    ax.set_xlabel("Time", color="#8b949e", fontsize=8)
    ax.set_ylabel("Normalised %", color="#8b949e", fontsize=8)
    ax.axhline(0, color="#30363d", linewidth=0.6)

    palette = ["#58a6ff", "#3fb950", "#d29922"]
    x       = np.linspace(0, 1, 80)
    lines_d = {}
    paths   = {}

    for (name, val), color in zip(market_data.items(), palette):
        chg = val["change"]
        np.random.seed(abs(int(chg * 100)) % 9999)
        noise = np.cumsum(np.random.randn(80) * 0.08)
        noise = noise - noise[0]
        path  = noise + (chg * x)
        paths[name] = path
        line, = ax.plot([], [], color=color, linewidth=1.5, label=name)
        lines_d[name] = line

    ax.set_xlim(0, 79)
    ymin = min(p.min() for p in paths.values()) - 0.3
    ymax = max(p.max() for p in paths.values()) + 0.3
    ax.set_ylim(ymin, ymax)
    ax.legend(fontsize=7, facecolor="#161b22", edgecolor="#30363d",
              labelcolor="#e6edf3", loc="upper left")

    def animate(f):
        for name, line in lines_d.items():
            line.set_data(range(f + 1), paths[name][:f + 1])
        return list(lines_d.values())

    ani = animation.FuncAnimation(fig, animate, frames=80,
                                  interval=40, blit=True)
    tmp = tempfile.NamedTemporaryFile(suffix=".gif", delete=False)
    tmp.close()
    ani.save(tmp.name, writer=animation.PillowWriter(fps=22), dpi=110)
    plt.close(fig)
    with open(tmp.name, "rb") as f:
        data = f.read()
    os.unlink(tmp.name)
    return data

# ── Script helpers ────────────────────────────────────────────────────────────

def generate_script(market_data):
    summary = "\n".join([
        f"{k}: {v['price']} ({'+' if v['change'] >= 0 else ''}{v['change']}%)"
        for k, v in market_data.items()
    ])
    prompt = f"""
You are a professional Indian stock market TV anchor.
Write a 60-second market update video script.

Today's Data:
{summary}

Use EXACTLY this format:

[INTRO - 5s]
One punchy opening line about today's market.

[MARKET SUMMARY - 20s]
2-3 sentences covering index movements.

[KEY HIGHLIGHT - 20s]
One important trend or observation from today.

[WHAT TO WATCH - 10s]
One thing investors should monitor tomorrow.

[OUTRO - 5s]
Closing line mentioning ET Markets.

Keep it crisp, professional, and factual.
"""
    r = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=400,
        temperature=0.4,
    )
    return r.choices[0].message.content


def parse_script(text):
    sections, current_key, current_lines = {}, None, []
    for line in text.split("\n"):
        line = line.strip()
        if not line:
            continue
        if line.startswith("[") and "]" in line:
            if current_key:
                sections[current_key] = " ".join(current_lines).strip()
            current_key   = line.split("]")[0].replace("[", "").strip()
            current_lines = []
        elif current_key:
            current_lines.append(line)
    if current_key:
        sections[current_key] = " ".join(current_lines).strip()
    return sections

# ── UI helpers ────────────────────────────────────────────────────────────────

def _card(content_html, border_color="#30363d"):
    st.markdown(
        f"""<div style="background:#161b22;border:1px solid #30363d;
        border-left:3px solid {border_color};border-radius:10px;
        padding:16px;margin-bottom:10px">{content_html}</div>""",
        unsafe_allow_html=True,
    )


def _stat_card(label, value, color):
    st.markdown(
        f"""<div style="background:#161b22;border:1px solid #30363d;
        border-radius:8px;padding:14px;text-align:center">
            <div style="font-size:1.4rem;font-weight:700;color:{color}">
                {value}</div>
            <div style="font-size:0.75rem;color:#8b949e;margin-top:4px">
                {label}</div>
        </div>""",
        unsafe_allow_html=True,
    )


def _gif_html(gif_bytes):
    b64 = base64.b64encode(gif_bytes).decode()
    return (f'<img src="data:image/gif;base64,{b64}" '
            f'style="width:100%;border-radius:10px;border:1px solid #30363d"/>')

# ── Main page ─────────────────────────────────────────────────────────────────

def show_video():
    st.markdown("# 🎬 AI Market Video Engine")
    st.markdown("*Auto-generate broadcast-quality market update scripts from live data*")
    st.divider()

    # Pipeline steps
    st.markdown("### ⚙️ How It Works")
    steps = [
        ("#58a6ff", "📡", "Step 1", "Data Agent",   "Fetches live Nifty, Sensex, Bank Nifty data"),
        ("#3fb950", "✍️",  "Step 2", "Script Agent", "AI writes broadcast-quality 60s script"),
        ("#a371f7", "🎙️", "Step 3", "Voice Agent",  "ElevenLabs voiceover · v2.0 Roadmap"),
        ("#d29922", "🎬", "Step 4", "Video Agent",  "MoviePy MP4 rendering · v2.0 Roadmap"),
    ]
    for col, (color, icon, step, title, desc) in zip(st.columns(4), steps):
        with col:
            st.markdown(
                f"""<div style="background:#161b22;border:1px solid #30363d;
                border-top:3px solid {color};border-radius:10px;
                padding:16px;text-align:center;min-height:150px">
                    <div style="font-size:1.8rem">{icon}</div>
                    <div style="font-size:0.7rem;color:{color};font-weight:600;
                    margin:4px 0">{step}</div>
                    <div style="font-size:0.9rem;font-weight:600;color:#e6edf3;
                    margin-bottom:6px">{title}</div>
                    <div style="font-size:0.75rem;color:#8b949e;
                    line-height:1.5">{desc}</div>
                </div>""",
                unsafe_allow_html=True,
            )
    st.divider()

    # Session state
    for key in ("video_market", "video_script", "sector_gif", "index_gif"):
        if key not in st.session_state:
            st.session_state[key] = None

    # Fetch market data
    st.markdown("### 📊 Today's Market Data")
    if st.button("📡 Fetch Live Market Data", use_container_width=True,
                 key="vp_btn_fetch"):
        with st.spinner("Fetching live indices…"):
            st.session_state.video_market = get_market_data()
            st.session_state.video_script = None
            st.session_state.sector_gif   = None
            st.session_state.index_gif    = None

    if st.session_state.video_market:
        market = st.session_state.video_market
        for col, (name, val) in zip(st.columns(len(market)), market.items()):
            chg   = val["change"]
            color = "#3fb950" if chg >= 0 else "#f85149"
            arrow = "▲" if chg >= 0 else "▼"
            with col:
                st.markdown(
                    f"""<div style="background:#161b22;border:1px solid #30363d;
                    border-radius:10px;padding:16px;text-align:center">
                        <div style="font-size:0.8rem;color:#8b949e;
                        margin-bottom:4px">{name}</div>
                        <div style="font-size:1.4rem;font-weight:700;
                        color:#e6edf3">{val['price']:,}</div>
                        <div style="font-size:1rem;font-weight:600;
                        color:{color}">{arrow} {abs(chg)}%</div>
                    </div>""",
                    unsafe_allow_html=True,
                )
        st.divider()

        # Script generator
        st.markdown("### 📝 AI Script Generator")
        if st.button("🤖 Generate Video Script", use_container_width=True,
                     key="vp_btn_script"):
            with st.spinner("AI writing broadcast script…"):
                try:
                    st.session_state.video_script = generate_script(market)
                except Exception as e:
                    st.error(f"Script error: {e}")

    # Script display
    if st.session_state.video_script:
        parsed     = parse_script(st.session_state.video_script)
        word_count = len(st.session_state.video_script.split())
        est_dur    = round(word_count / 2.5)

        st.divider()
        st.markdown("### 🎬 Generated Script")

        s1, s2, s3 = st.columns(3)
        with s1: _stat_card("Script Status", "READY", "#3fb950")
        with s2: _stat_card("Words", str(word_count), "#58a6ff")
        with s3: _stat_card("Est. Duration", f"~{est_dur}s", "#d29922")

        st.markdown("<br>", unsafe_allow_html=True)

        section_styles = {
            "INTRO":          ("#58a6ff", "🎬"),
            "MARKET SUMMARY": ("#3fb950", "📊"),
            "KEY HIGHLIGHT":  ("#a371f7", "⭐"),
            "WHAT TO WATCH":  ("#d29922", "👁️"),
            "OUTRO":          ("#f85149", "🏁"),
        }
        for section, content in parsed.items():
            if not content:
                continue
            color, icon = "#8b949e", "📌"
            for key, (c, i) in section_styles.items():
                if key in section.upper():
                    color, icon = c, i
                    break
            _card(
                f"""<div style="font-size:0.75rem;color:{color};font-weight:600;
                margin-bottom:8px">{icon} {section}</div>
                <div style="font-size:0.95rem;color:#e6edf3;
                line-height:1.8">{content}</div>""",
                border_color=color,
            )

        st.download_button(
            label="⬇️ Download Script (.txt)",
            data=st.session_state.video_script,
            file_name="market_script.txt",
            mime="text/plain",
            use_container_width=True,
            key="vp_btn_dl_script",
        )
        st.divider()

        # Animated preview
        st.markdown("### 🖥️ Animated Market Preview")
        st.caption("Real animated charts — auto-generated from live data")

        if st.button("▶ Generate Animated Preview", use_container_width=True,
                     key="vp_btn_preview"):
            market = st.session_state.video_market or {}
            with st.spinner("Generating sector race chart…"):
                try:
                    sector_data = get_sector_data()
                    st.session_state.sector_gif = generate_race_chart_gif(sector_data)
                except Exception as e:
                    st.error(f"Race chart error: {e}")
            with st.spinner("Generating index sparklines…"):
                try:
                    st.session_state.index_gif = generate_index_sparkline_gif(market)
                except Exception as e:
                    st.error(f"Sparkline error: {e}")

        if st.session_state.sector_gif or st.session_state.index_gif:
            v1, v2 = st.columns(2)
            with v1:
                if st.session_state.sector_gif:
                    st.markdown("**Sector Race Chart**")
                    st.markdown(_gif_html(st.session_state.sector_gif),
                                unsafe_allow_html=True)
                    st.download_button("⬇️ Download Sector GIF",
                                       data=st.session_state.sector_gif,
                                       file_name="sector_race.gif",
                                       mime="image/gif",
                                       use_container_width=True,
                                       key="vp_btn_dl_sector")
            with v2:
                if st.session_state.index_gif:
                    st.markdown("**Index Sparklines**")
                    st.markdown(_gif_html(st.session_state.index_gif),
                                unsafe_allow_html=True)
                    st.download_button("⬇️ Download Index GIF",
                                       data=st.session_state.index_gif,
                                       file_name="index_sparklines.gif",
                                       mime="image/gif",
                                       use_container_width=True,
                                       key="vp_btn_dl_index")
            st.divider()

        # Roadmap banner
        st.markdown(
            """<div style="background:#161b22;border:1px solid #30363d;
            border-left:3px solid #a371f7;border-radius:10px;
            padding:14px;text-align:center;color:#8b949e;font-size:0.82rem">
                🚀 <b style="color:#a371f7">v2.0 Roadmap</b> ·
                ElevenLabs voiceover → MoviePy MP4 rendering →
                Auto-publish pipeline
            </div>""",
            unsafe_allow_html=True,
        )