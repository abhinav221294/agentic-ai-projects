from utils.llm import get_llm

def analyze_portfolio(payload: dict) -> str:
    if not payload:
        return "Portfolio data not available."

    llm = get_llm()

    prompt = f"""
    You are a professional financial advisor.

    Analyze the following investment portfolio:

    Total Value: ₹{payload.get("total_value")}

    Holdings:
    {payload.get("holdings")}

    Risk Distribution:
    {payload.get("risk_distribution")}

    Provide:
    - Risk analysis
    - Diversification feedback
    - Portfolio weaknesses
    - Clear actionable suggestions

    Keep response concise (120-180 words) and practical.
    """

    try:
        response = llm.invoke(prompt)
        return response.content.strip()
    except:
        return "Portfolio analysis failed."