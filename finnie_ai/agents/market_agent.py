from utils.state import AgentState
import yfinance as yf
import os
import requests
from utils.stock_mapper import STOCK_MAP
import re
import time


def normalize_for_provider(symbol, provider):
    if provider == "finnhub":
        return symbol.replace(".NS", "")
    if provider == "alpha":
        return symbol.replace(".NS", ".BSE")
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
            return {"current": current_price, "previous": previous_close}

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


# -------------------------
# CENTRAL RESPONSE SETTER
# -------------------------
def _set(state, start, answer, confidence, decision_source, answer_source, extra=None):
    state["answer"] = answer
    state["agent"] = "market_agent"
    state["confidence"] = confidence
    state["decision_source"] = decision_source
    state["answer_source"] = answer_source
    state["execution_time"] = round(time.time() - start, 2)

    if extra:
        state.update(extra)

    return state


def market_agent(state: AgentState) -> AgentState:
    start = time.time()
    memory = state.get("memory", [])
    raw_query = state["query"]
    query = re.sub(r"[^a-zA-Z0-9\s]", "", raw_query.lower())


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
    for key, val in sorted(STOCK_MAP.items(), key=lambda x: -len(x[0])):
        key_words = key.lower().split()

        if any(word in query for word in key_words):
            symbol = val
            company_name = key.title()
            break

    if not symbol:
        return _set(
            state, start,
            "Sorry, I couldn't identify the stock. Try Tesla, Apple, Reliance, TCS.",
            0.4, "rule", "none"
        )

    price = None
    trend = "Not enough data"
    source = None

    # -------------------------
    # YFINANCE
    # -------------------------
    try:
        session = requests.Session()
        session.headers.update({"User-Agent": "Mozilla/5.0"})

        stock = yf.Ticker(symbol, session=session)
        hist = stock.history(period="5d", interval="1d")

        if not hist.empty and "Close" in hist:
            price = hist["Close"].iloc[-1]

            if len(hist) >= 2:
                trend = "📈 Up" if hist["Close"].iloc[-1] > hist["Close"].iloc[-2] else "📉 Down"
            else:
                trend = "No major movement"

            source = "yfinance"

    except Exception as e:
        print(f"yfinance error: {e}")

    # -------------------------
    # FALLBACK: FINNHUB + ALPHA
    # -------------------------
    if price is None:
        price_data = get_finnhub_price(symbol, previous=True)

        if not price_data:
            alpha_price = get_alpha_vantage_price(symbol)

            if not alpha_price:
                return _set(
                state, start,
                f"Couldn't fetch price for {company_name} right now.",
                0.4,
                "tool",
                "none"
                )

            price = alpha_price
            trend = "No trend data"
            source = "Alpha Vantage"

        else:
            current = price_data.get("current")
            previous = price_data.get("previous")
            
            if current:
                price = current

                if previous:
                    change = current - previous
                    pct = (change / previous) * 100

                    trend = "📈 Up" if change > 0 else "📉 Down"
                    trend += f" ({pct:.2f}%)"
                else:
                    trend = "No trend data"
                
                if abs(pct) < 1:
                    trend = "sideways"
                elif pct > 0:
                    trend = "uptrend"
                else:
                    trend = "downtrend"

                state.update({
                    "market_trend_type": trend
                })

                source = "Finnhub"

    # -------------------------
    # RESPONSE
    # -------------------------
    source_map = {
        "yfinance": "yfinance",
        "Finnhub": "finnhub",
        "Alpha Vantage": "alpha_vantage"
    }
    normalized_source = source_map.get(source, "unknown")

    if price:
        tools = state.setdefault("tools_used", [])

        if source == "yfinance" and "yfinance" not in tools:
            tools.append("yfinance")
        elif source == "Finnhub" and "finnhub" not in tools:
            tools.append("finnhub")
        elif source == "Alpha Vantage" and "alpha_vantage" not in tools:
            tools.append("alpha_vantage")

        currency = "₹" if symbol.endswith(".NS") else "$"

        answer = (
            f"{company_name} ({symbol}) is trading at {currency}{round(price, 2)}\n"
            f"Trend: {trend}\n"
            f"(Source: {source})"
        )

        return _set(
        state, start,
        answer,
        0.9 if normalized_source == "yfinance" else 0.7,
        "tool",
        normalized_source,
        extra={
            "market_symbol": symbol,
            "market_company": company_name,
            "market_price": price,
            "market_trend": trend,
            "market_source": normalized_source
            }
        )
    
    # -------------------------
    # FAILURE
    # -------------------------
    return _set(
        state, start,
        f"I'm unable to fetch stock data for {company_name} right now.\nPlease try again shortly.",
        0.4,
        "tool",
        "none",
        {"error": "price_fetch_failed"}
    )