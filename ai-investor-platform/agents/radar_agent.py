import yfinance as yf
from groq import Groq
import os

class RadarAgent:
    """
    Opportunity Radar Agent.
    Scans NSE stocks for unusual signals and ranks them.
    """

    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = "llama-3.3-70b-versatile"
        self.watchlist = [
            "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS",
            "ICICIBANK.NS", "SBIN.NS", "BHARTIARTL.NS", "ITC.NS",
            "KOTAKBANK.NS", "LT.NS", "AXISBANK.NS", "WIPRO.NS",
            "MARUTI.NS", "TITAN.NS", "BAJFINANCE.NS"
        ]

    def scan_stock(self, ticker):
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="30d")
            if hist.empty or len(hist) < 5:
                return None

            current = hist['Close'].iloc[-1]
            prev5 = hist['Close'].iloc[-6]
            change5d = round(((current - prev5) / prev5) * 100, 2)

            avg_vol = hist['Volume'].iloc[:-1].mean()
            curr_vol = hist['Volume'].iloc[-1]
            vol_spike = round((curr_vol / avg_vol) * 100, 1)

            score = 0
            signals = []

            if vol_spike > 200:
                score += 3
                signals.append(f"Volume spike {vol_spike}% above average")
            elif vol_spike > 150:
                score += 2
                signals.append(f"High volume {vol_spike}% above average")

            if change5d > 8:
                score += 3
                signals.append(f"Strong rally +{change5d}% in 5 days")
            elif change5d > 4:
                score += 2
                signals.append(f"Positive momentum +{change5d}%")
            elif change5d < -8:
                score += 2
                signals.append(f"Sharp decline {change5d}%")

            return {
                "ticker": ticker.replace(".NS", ""),
                "price": round(current, 2),
                "change5d": change5d,
                "vol_spike": vol_spike,
                "score": score,
                "signals": signals
            }
        except:
            return None

    def run(self, data=None) -> dict:
        results = []
        for ticker in self.watchlist:
            result = self.scan_stock(ticker)
            if result and result['score'] > 0:
                results.append(result)

        results.sort(key=lambda x: x['score'], reverse=True)

        return {
            "agent": "RadarAgent",
            "stocks_scanned": len(self.watchlist),
            "signals_found": len(results),
            "top_signals": results[:5]
        }