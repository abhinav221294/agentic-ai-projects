from utils.state import AgentState
import yfinance as yf
import os
import requests
from utils.stock_mapper import STOCK_MAP
import re


def normalize_for_provider(symbol, provider):
    if provider == "finnhub":
        return symbol.replace(".NS", "")  # RELIANCE
    if provider == "alpha":
        return symbol.replace(".NS", ".BSE")  # RELIANCE.BSE
    return symbol


def get_finnhub_price(symbol: str, previous=False):
    api_key = os.getenv("FINNHUB_API_KEY")
    if not api_key:
        return None
    
    try:
        symbol = normalize_for_provider(symbol, "finnhub")
        url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={api_key}"
        response = requests.get(url, timeout=5)
        data = response.json()
        
        current_price = data.get("c")
        previous_close = data.get("pc")

        if previous:
              return {
                "current": current_price,
                "previous": previous_close
            }
        return current_price
    except:
        return None
    
def get_alpha_vantage_price(symbol: str):

    api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
    if not api_key:
        return None
    try:
        symbol = normalize_for_provider(symbol, "alpha")
        url = "https://www.alphavantage.co/query"
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": symbol,
            "apikey": api_key
            }
        response = requests.get(url, params=params, timeout=5) 
        data = response.json()

        price = data.get("Global Quote", {}).get("05. price")
        return float(price) if price else None
    except:
        return None

def market_agent(state: AgentState) -> AgentState:

    # -------------------------
    # Step 1: Clean query
    # -------------------------
    raw_query = state["query"]
    query = re.sub(r"[^a-zA-Z0-9\s]", "", raw_query.lower())

    # -------------------------
    # Step 2: Detect stock
    # -------------------------
    symbol = None
    company_name = None

    query_words = query.split()

    for key, val in sorted(STOCK_MAP.items(), key=lambda x: -len(x[0])):
        key_words = key.lower().split()

        if all(word in query_words for word in key_words):
            symbol = val
            company_name = key.title()
            break

    if not symbol:
        state["answer"] = "Sorry, I couldn't identify the stock. Try Tesla, Apple, Reliance, TCS."
        state["agent"] = "market_agent"
        return state

    price = None
    trend = "unknown"
    source = None

    # -------------------------
    # Step 3: Try yfinance
    # -------------------------
    try:
        session = requests.Session()
        session.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36"})

        stock = yf.Ticker(symbol, session=session)

        hist = stock.history(period="5d", interval="1d")

        if not hist.empty and "Close" in hist:
            price = hist["Close"].iloc[-1]

            if len(hist) >= 2:
                trend = "📈 Up" if hist["Close"].iloc[-1] > hist["Close"].iloc[-2] else "📉 Down"
            else:
                trend = "stable"

            source = "yfinance"

    except Exception as e:
        print(f"yfinance error: {e}")

    # -------------------------
    # Step 4: Finnhub fallback
    # -------------------------
    if price is None:
        data = get_finnhub_price(symbol, previous=True)

        if data and data.get("current"):
            price = data["current"]
            prev = data.get("previous", 0)

            trend = "📈 Up" if price > prev else "📉 Down"
            source = "Finnhub"

    # -------------------------
    # Step 5: Alpha fallback
    # -------------------------
    if price is None:
        alpha_price = get_alpha_vantage_price(symbol)

        if alpha_price:
            price = alpha_price
            trend = "unknown"
            source = "Alpha Vantage"

    # -------------------------
    # Step 6: Final response
    # -------------------------
    if price:
        currency = "₹" if symbol.endswith(".NS") else "$"

        state["answer"] = (
            f"{company_name} ({symbol}) is trading at {currency}{round(price, 2)}\n"
            f"Trend: {trend}\n"
            f"(Source: {source})"
        )

        state["agent"] = "market_agent"
        state["confidence"] = "HIGH" if source == "yfinance" else "MEDIUM"
        return state

    # -------------------------
    # Step 7: Failure
    # -------------------------
    state["answer"] = (
        f"I couldn't fetch stock data for {company_name} right now.\n"
        "Please try again later."
    )

    state["agent"] = "market_agent"
    state["confidence"] = "LOW"
    return state