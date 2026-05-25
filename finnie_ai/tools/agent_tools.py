# Import decorator to register functions as LangChain tools
from langchain.tools import tool

# Import different agents responsible for specific domains
from agents.market_agent import market_agent
from agents.risk_agent import risk_agent
from agents.news_agent import news_agent
from agents.rag_agent import rag_agent


# -------------------------
# MARKET TOOL
# -------------------------
@tool
def market_tool(state: dict):
    """
    Fetch stock price or market-related data.

    This tool:
    - Calls the market_agent
    - Extracts the final answer from agent state
    """

    # Pass the full state to market agent
    result = market_agent(state)

    # Return only the answer field (clean output for tool usage)
    return result.get("answer")


# -------------------------
# RISK TOOL
# -------------------------
@tool
def risk_tool(state: dict):
    """
    Analyze financial risk based on query.

    This tool:
    - Calls the risk_agent
    - Returns interpreted risk insights
    """

    # Execute risk analysis agent
    result = risk_agent(state)

    # Extract and return response
    return result.get("answer")


# -------------------------
# NEWS TOOL
# -------------------------
@tool
def news_tool(state: dict):
    """
    Fetch latest financial news.

    This tool:
    - Calls the news_agent
    - Returns summarized news output
    """

    # Execute news agent
    result = news_agent(state)

    # Return formatted news summary
    return result.get("answer")


# -------------------------
# RAG TOOL
# -------------------------
@tool
def rag_tool(state: dict):
    """
    Retrieve financial concepts or definitions.

    This tool:
    - Calls the rag_agent
    - Returns retrieved knowledge from documents
    """

    # Execute retrieval-based agent
    result = rag_agent(state)

    # Return extracted answer
    return result.get("answer")