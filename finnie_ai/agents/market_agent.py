# -------------------------
# IMPORTS
# -------------------------
# Agent state schema (shared across system)
from utils.state import AgentState

# yfinance for stock price data (primary source)
import yfinance as yf

# OS for environment variables (API keys)
import os

# requests for API calls (Finnhub, Alpha Vantage)
import requests

# Stock mapping utility (maps company names → symbols)
from utils.stock_mapper import STOCK_MAP

# Regex for query cleaning
import re

# Time tracking for execution metrics
import time

from utils.state_utils import set_state


# -------------------------
# SYMBOL NORMALIZATION
# -------------------------
def normalize_for_provider(symbol, provider):
    """
    Adjusts stock symbol format depending on data provider.

    Example:
    - Finnhub uses plain symbols (remove .NS)
    - Alpha Vantage uses .BSE instead of .NS
    """
    if provider == "finnhub":
        return symbol.replace(".NS", "")
    if provider == "alpha":
        return symbol.replace(".NS", ".BSE")
    return symbol


# -------------------------
# FINNHUB API
# -------------------------
def get_finnhub_price(symbol: str, previous=False):
    """
    Fetch stock price from Finnhub API.

    Parameters:
    - symbol: stock symbol
    - previous: whether to include previous close price

    Returns:
    - current price OR dict with current + previous price
    """
    api_key = os.getenv("FINNHUB_API_KEY")

    # If API key missing → skip
    if not api_key:
        return None

    try:
        # Normalize symbol format
        symbol = normalize_for_provider(symbol, "finnhub")

        # Build API URL
        url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={api_key}"

        # Make request with timeout protection
        response = requests.get(url, timeout=5)
        data = response.json()

        # Extract current and previous close
        current_price = data.get("c")
        previous_close = data.get("pc")

        

        # Return based on flag
        if previous:
            return {"current": current_price, "previous": previous_close}

        return current_price

    except:
        # Fail-safe return
        return None


# -------------------------
# ALPHA VANTAGE API
# -------------------------
def get_alpha_vantage_price(symbol: str):
    """
    Fetch stock price from Alpha Vantage (fallback API).
    """
    api_key = os.getenv("ALPHA_VANTAGE_API_KEY")

    if not api_key:
        return None

    try:
        # Normalize symbol format
        symbol = normalize_for_provider(symbol, "alpha")

        # API endpoint + params
        url = "https://www.alphavantage.co/query"
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": symbol,
            "apikey": api_key
        }

        # Send request
        response = requests.get(url, params=params, timeout=5)
        data = response.json()

        # Extract price
        price = data.get("Global Quote", {}).get("05. price")

        return float(price) if price else None

    except:
        return None


def market_agent(state: AgentState) -> AgentState:
    """
    Main market agent:
    - Detects stock from query
    - Fetches price using multiple providers
    - Calculates trend
    - Returns formatted response
    """

    # Start timer
    start = time.time()

    # Retrieve conversation memory
    memory = state.get("memory", [])

    # Clean query (remove special characters, lowercase)
    raw_query = state["query"]
    query = re.sub(r"[^a-zA-Z0-9\s]", "", raw_query.lower())


    # -------------------------
    # FOLLOW-UP HANDLING
    # -------------------------
    # If query is short → append last query for context
    if memory and len(query.split()) <= 3:
        last_query = next(
            (m.get("query", "") for m in reversed(memory) if m.get("query")),
            ""
        )
        query = f"{last_query} {query}"


    symbol = None
    company_name = None

    # -------------------------
    # STOCK DETECTION
    # -------------------------
    # Match query with known stock names
    # Sorting ensures longer names match first (better accuracy)
    for key, val in sorted(STOCK_MAP.items(), key=lambda x: -len(x[0])):
        key_words = key.lower().split()

        # Check if any keyword matches query
        if any(word in query for word in key_words):
            symbol = val
            company_name = key.title()
            break

    # If no stock detected → return fallback
    if not symbol:
        return set_state(
        state,
        start,
        answer="Sorry, I couldn't identify the stock. Try Tesla, Apple, Reliance, TCS.",
        agent="market_agent",
        confidence=0.4,
        decision_source="rule",
        answer_source="rule",
        trace_action="stock_not_found"
        )       


    # Initialize variables
    price = None
    trend = "Not enough data"
    source = None


    # -------------------------
    # PRIMARY SOURCE: YFINANCE
    # -------------------------
    try:
        # Create session with headers (prevents blocking)
        session = requests.Session()
        session.headers.update({"User-Agent": "Mozilla/5.0"})

        # Fetch stock object
        stock = yf.Ticker(symbol, session=session)

        if not symbol:
            return set_state(
            state,
            start,
            answer="Stock symbol is missing. Please try again.",
            agent="market_agent",
            confidence=0.3,
            decision_source="rule",
            answer_source="none",
            trace_action="symbol_none"
            )

        # Get last 5 days data
        hist = stock.history(period="5d", interval="1d")

        if not hist.empty and "Close" in hist:
            # Latest closing price
            price = hist["Close"].iloc[-1]

            # Determine trend based on previous day
            if len(hist) >= 2:
                trend = "📈 Up" if hist["Close"].iloc[-1] > hist["Close"].iloc[-2] else "📉 Down"
            else:
                trend = "No major movement"

            source = "yfinance"

    except Exception as e:
        # Log error (non-blocking)
        print(f"yfinance error: {e}")


    # -------------------------
    # FALLBACK: FINNHUB + ALPHA
    # -------------------------
    if price is None:
        price_data = get_finnhub_price(symbol, previous=True)

        if not price_data:
            # Try Alpha Vantage as last fallback
            alpha_price = get_alpha_vantage_price(symbol)

            if not alpha_price:
                return set_state(
                state,
                start,
                answer=f"Couldn't fetch price for {company_name} right now.",
                agent="market_agent",
                confidence=0.4,
                decision_source="tool",
                answer_source="none",
                trace_action="api_failure"
                )

            price = alpha_price
            trend = "No trend data"
            source = "Alpha Vantage"

        else:
            current = price_data.get("current")
            previous = price_data.get("previous")
            
            if current:
                price = current

                # Calculate price change %
                if previous:
                    change = current - previous
                    pct = (change / previous) * 100

                    trend = "📈 Up" if change > 0 else "📉 Down"
                    trend += f" ({pct:.2f}%)"
                
                    # Simplify trend into categories
                    if abs(pct) < 1:
                        trend = "sideways"
                    elif pct > 0:
                        trend = "uptrend"
                    else:
                        trend = "downtrend"
                        
                else:
                    trend = "No trend data"

                # Store structured trend type
                state.update({
                    "market_trend_type": trend
                })

                source = "Finnhub"


    # -------------------------
    # RESPONSE BUILDING
    # -------------------------
    # Normalize source name
    source_map = {
        "yfinance": "yfinance",
        "Finnhub": "finnhub",
        "Alpha Vantage": "alpha_vantage"
    }
    normalized_source = source_map.get(source, "unknown")

    if price:
        # Track tools used (for observability)
        tools = state.setdefault("tools_used", [])

        if source == "yfinance" and "yfinance" not in tools:
            tools.append("yfinance")
        elif source == "Finnhub" and "finnhub" not in tools:
            tools.append("finnhub")
        elif source == "Alpha Vantage" and "alpha_vantage" not in tools:
            tools.append("alpha_vantage")

        # Currency selection based on exchange
        currency = "₹" if symbol.endswith(".NS") else "$"
        

        # Final formatted answer
        answer = (
            f"{company_name} ({symbol}) is trading at {currency}{round(price, 2)}\n"
            f"Trend: {trend}\n"
            f"(Source: {source})"
        )

        return set_state(
        state,
        start,
        answer=answer,
        agent="market_agent",
        confidence=0.9 if normalized_source == "yfinance" else 0.7,
        decision_source="tool",
        answer_source=normalized_source,
        trace_action="fetch_price",
        extra={
        "market_symbol": symbol,
        "market_company": company_name,
        "market_price": price,
        "market_trend": trend,
        "market_source": normalized_source
        }
    )
    

    # -------------------------
    # FAILURE HANDLING
    # -------------------------
    return set_state(
        state,
        start,
        answer=f"I'm unable to fetch stock data for {company_name} right now.\nPlease try again shortly.",
        agent="market_agent",
        confidence=0.4,
        decision_source="tool",
        answer_source="none",
        trace_action="error",
        extra={
        "error": "price_fetch_failed",
        "error_source": "market_api",
        "error_stage": state.get("stage")
        }
    )