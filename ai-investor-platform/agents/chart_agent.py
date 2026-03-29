import yfinance as yf
import ta
from groq import Groq
import os

class ChartAgent:
    """
    Chart Pattern Intelligence Agent.
    Detects RSI, Moving Average, and Bollinger Band patterns.
    """

    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = "llama-3.3-70b-versatile"

    def run(self, data: dict) -> dict:
        ticker = data.get("ticker", "")
        if not ticker:
            return {"error": "No ticker provided"}

        try:
            stock = yf.Ticker(ticker + ".NS")
            hist = stock.history(period="6mo")
            if hist.empty:
                return {"error": f"No data found for {ticker}"}

            hist['RSI'] = ta.momentum.RSIIndicator(
                hist['Close'], window=14).rsi()
            hist['MA20'] = hist['Close'].rolling(20).mean()
            hist['MA50'] = hist['Close'].rolling(50).mean()

            latest = hist.iloc[-1]
            rsi = round(latest['RSI'], 1)
            ma20 = round(latest['MA20'], 2)
            ma50 = round(latest['MA50'], 2)
            price = round(latest['Close'], 2)

            patterns = []
            if rsi >= 70:
                patterns.append("RSI Overbought — possible pullback")
            elif rsi <= 30:
                patterns.append("RSI Oversold — possible bounce")

            if ma20 > ma50:
                patterns.append("Bullish trend — MA20 above MA50")
            else:
                patterns.append("Bearish trend — MA20 below MA50")

            prompt = f"""
Stock: {ticker}, Price: ₹{price}, RSI: {rsi}
MA20: ₹{ma20}, MA50: ₹{ma50}
Patterns: {', '.join(patterns)}

In 3 lines explain this to a beginner investor.
What to do: buy, hold, or wait? Be specific.
"""
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.3
            )

            return {
                "agent": "ChartAgent",
                "ticker": ticker,
                "price": price,
                "rsi": rsi,
                "ma20": ma20,
                "ma50": ma50,
                "patterns": patterns,
                "explanation": response.choices[0].message.content
            }

        except Exception as e:
            return {"error": str(e)}