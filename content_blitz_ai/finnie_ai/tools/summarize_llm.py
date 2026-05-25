# Import LLM utility function to initialize the language model
from utils.llm import get_llm

llm = get_llm(
    temperature=0.1,
    max_tokens=220
    )

def analyze_portfolio(payload: dict) -> str:
    """
    Analyzes a user's investment portfolio using an LLM.

    Parameters:
    - payload (dict): Contains portfolio details such as:
        - total_value: Total portfolio value
        - holdings: List or breakdown of investments
        - risk_distribution: Allocation across risk categories

    Returns:
    - str: LLM-generated portfolio analysis
    """

    # -------------------------
    # INPUT VALIDATION
    # -------------------------
    # Check if payload is empty or None
    # This prevents sending empty data to LLM
    if not payload:
        return "Portfolio data not available."

    # -------------------------
    # INITIALIZE LLM
    # -------------------------
    # Initialize LLM with default configuration
    # (temperature, model, etc. handled inside get_llm)
  

    # -------------------------
    # PROMPT CONSTRUCTION
    # -------------------------
    # Create a structured prompt for financial analysis
    # Using f-string to dynamically inject portfolio data
    prompt = f"""You are a professional financial advisor.
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
Keep response concise (100-120 words) and practical."""

    # -------------------------
    # LLM INVOCATION
    # -------------------------
    try:
        # Send prompt to LLM and receive response object
        response = llm.invoke(prompt)

        # Extract text content and remove leading/trailing whitespace
        answer = response.content.strip()
        answer = " ".join(answer.split())


        return answer

    # -------------------------
    # ERROR HANDLING
    # -------------------------
    except Exception as e:
        print("Portfolio analysis error:", e)
        return "Portfolio analysis failed."
    

def summarize_article(content: str) -> str:
    """
    Summarizes a news article using an LLM.

    Parameters:
    - content (str): Raw article text

    Returns:
    - str: Concise summary (120–180 words)
    """

    # -------------------------
    # INPUT VALIDATION
    # -------------------------
    # Ensure content is not empty or None
    if not content:
        return "Summary not available."

    # -------------------------
    # INITIALIZE LLM
    # -------------------------
    # Slightly higher temperature for better narrative flow
    # while still maintaining factual consistency

    # -------------------------
    # PROMPT CONSTRUCTION
    # -------------------------
    # Define clear instructions for summarization
    prompt = f"""Summarize the following news article in 60-90 words.
Focus on:
- Main event
- Market/business impact
- Key investor takeaway

Keep concise and practical.
Article:
{content}"""
    # -------------------------
    # LLM INVOCATION
    # -------------------------
    try:
        # Call LLM with the prompt
        response = llm.invoke(prompt)

        if len(content.split()) < 40:
            return "Article content too limited for reliable summary."
        
        # Return cleaned summary text
        return response.content.strip()

    # -------------------------
    # ERROR HANDLING
    # -------------------------
    except Exception as e:
        print("Summary generation error:", e)
        return "Summary generation failed."