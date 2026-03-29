from groq import Groq
import os

from dotenv import load_dotenv
import os

load_dotenv()

class PortfolioAgent:
    """
    Portfolio Analyzer Agent.
    Analyzes mutual fund portfolio and generates recommendations.
    """

    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = "llama-3.3-70b-versatile"

    def run(self, portfolio_data: list) -> dict:
        if not portfolio_data:
            return {"error": "No portfolio data provided"}

        total = sum(f['amount'] for f in portfolio_data)
        summary = f"Total invested: ₹{total:,.0f}\n"
        summary += f"Number of funds: {len(portfolio_data)}\n\nFunds:\n"
        for f in portfolio_data:
            pct = round((f['amount'] / total) * 100, 1)
            summary += f"- {f['fund_name']}: ₹{f['amount']:,.0f} ({pct}%)\n"

        prompt = f"""
You are an expert Indian financial advisor.
Analyze this mutual fund portfolio and give clear recommendations.

{summary}

Format your response as:
## Portfolio Health Score: X/10
## Key Problems Found:
- problem 1
- problem 2
## What You Are Doing Right:
- good point 1
## Specific Recommendations:
1. recommendation
2. recommendation
## Bottom Line:
One powerful action sentence.
"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000,
            temperature=0.3
        )

        return {
            "agent": "PortfolioAgent",
            "total_invested": total,
            "fund_count": len(portfolio_data),
            "analysis": response.choices[0].message.content
        }