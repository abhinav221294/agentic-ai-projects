# Import LLM utility function to initialize the language model
from utils.llm import get_llm

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
    llm = get_llm()

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
Keep response concise (120-180 words) and practical."""

    # -------------------------
    # LLM INVOCATION
    # -------------------------
    try:
        # Send prompt to LLM and receive response object
        response = llm.invoke(prompt)

        # Extract text content and remove leading/trailing whitespace
        return response.content.strip()

    # -------------------------
    # ERROR HANDLING
    # -------------------------
    except:
        # If LLM call fails (network/API issue), return fallback message
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
    llm = get_llm(temperature=0.3)

    # -------------------------
    # PROMPT CONSTRUCTION
    # -------------------------
    # Define clear instructions for summarization
    prompt = f"""Summarize the following news article in 120-180 words.
Focus on:
- Key event
- Business/financial impact
- Important facts
Article:
{content}"""
    # -------------------------
    # LLM INVOCATION
    # -------------------------
    try:
        # Call LLM with the prompt
        response = llm.invoke(prompt)

        # Return cleaned summary text
        return response.content.strip()

    # -------------------------
    # ERROR HANDLING
    # -------------------------
    except:
        # Return fallback message if summarization fails
        return "Summary generation failed."