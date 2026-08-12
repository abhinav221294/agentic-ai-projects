import yfinance as yf
from agents.market_agent import get_finnhub_price
import streamlit as st
from utils.stock_mapper import normalize_stock


@st.cache_data(ttl=60)
def get_price(symbol):
    try:
        symbol = normalize_stock(symbol)

        if not symbol:
            return None

        # Indian stocks → Yahoo Finance
        if symbol.endswith(".NS"):
            data = yf.Ticker(symbol).history(period="5d")

            if data.empty or "Close" not in data.columns:
                return None

            close_prices = data["Close"].dropna()

            if close_prices.empty:
                return None

            return float(close_prices.iloc[-1])

        # US stocks → Finnhub
        price = get_finnhub_price(symbol)

        if price is not None:
            return float(price)

        return None

    except Exception as e:
        print("Price fetch error:", e)
        return None