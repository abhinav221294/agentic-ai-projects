import yfinance as yf
from agents.market_agent import get_finnhub_price
import streamlit as st

@st.cache_data(ttl=60)
def get_price(symbol):
    try:
        # ✅ Use yfinance for Indian stocks
        if symbol.endswith(".NS"):
            data = yf.Ticker(symbol).history(period="1d")
            if not data.empty:
                return float(data["Close"].iloc[-1])

        # ✅ Use Finnhub for US stocks
        price_data = get_finnhub_price(symbol)
        if price_data:
            return price_data.get("current")

        return None

    except Exception as e:
        print("Price fetch error:", e)
        return None