from langchain.tools import tool
from agents.market_agent import market_agent
from agents.risk_agent import risk_agent
from agents.news_agent import news_agent
from agents.rag_agent import rag_agent


@tool
def market_tool(state: dict):
    """Fetch stock price or market-related data."""
    result = market_agent(state)
    return result.get("answer")


@tool
def risk_tool(state: dict):
    """Analyze financial risk based on query."""
    result = risk_agent(state)
    return result.get("answer")


@tool
def news_tool(state: dict):
    """Fetch latest financial news."""
    result = news_agent(state)
    return result.get("answer")


@tool
def rag_tool(state: dict):
    """Retrieve financial concepts or definitions."""
    result = rag_agent(state)
    return result.get("answer")