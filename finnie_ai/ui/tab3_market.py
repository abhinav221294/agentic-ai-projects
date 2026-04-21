import streamlit as st
import yfinance as yf

from utils.stock_mapper import normalize_stock
from agents.market_agent import get_finnhub_price


def render_market_tab():

    st.title("📈 Market Trends")

    stock_input = st.text_input("Enter stock (e.g., Tesla, Apple, Reliance)")
    fetch_btn = st.button("🔍 Fetch Data")

    if stock_input and fetch_btn:

        symbol = normalize_stock(stock_input)

        with st.spinner("Fetching market data..."):
            try:
                data = yf.Ticker(symbol).history(period="1mo")

                if data.empty:
                    raise Exception("No data")

                # -------------------------
                # EXISTING CHART
                # -------------------------
                st.line_chart(data["Close"])

                latest = data["Close"].iloc[-1]
                prev_day = data["Close"].iloc[-2]

                change = latest - prev_day
                percent_change = (change / prev_day) * 100

                high_price = data["High"].max()
                low_price = data["Low"].min()

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric(
                        label=f"{symbol} Price",
                        value=round(latest, 2),
                        delta=f"{round(change,2)} ({round(percent_change,2)}%)"  # ✅ FIX: proper formatting
                    )

                with col2:
                    st.metric(
                        label="📈 Highest (1M)",
                        value=round(high_price, 2)
                    )

                with col3:
                    st.metric(
                        label="📉 Lowest (1M)",
                        value=round(low_price, 2)
                    )

                if change > 0:
                    st.success("📈 Stock is UP compared to yesterday")
                else:
                    st.error("📉 Stock is DOWN compared to yesterday")

                st.caption("📊 Based on last 1 month data")

            except Exception:
                price_data = get_finnhub_price(symbol, previous=True)

                if price_data:
                    current = price_data.get("current", 0)
                    prev = price_data.get("previous", 0)

                    if current is None:
                        st.error("❌ Market data unavailable (API issue)")
                    else:
                        change = (current - prev) if prev else 0

                        # -------------------------
                        # ✅ FIX 1: Restore warning banner
                        # -------------------------
                        st.warning("⚠️ Showing live price (chart unavailable)")

                        # -------------------------
                        # ✅ FIX 2: Restore 3-column layout
                        # -------------------------
                        col1, col2, col3 = st.columns(3)

                        with col1:
                            st.metric(
                                label=f"{symbol} Price",
                                value=round(current, 2),
                                delta=round(change, 2)  # ✅ FIX 3: rounded value
                            )

                        with col2:
                            st.metric(
                                label="📊 Data Source",
                                value="Finnhub"
                            )

                        with col3:
                            trend = "📈 Up" if change > 0 else "📉 Down"

                            st.metric(
                                label="Trend",
                                value=trend
                            )

                        # -------------------------
                        # ✅ FIX 4: Restore caption
                        # -------------------------
                        st.caption("⚠️ Chart data unavailable, showing real-time price only")

                else:
                    st.error("❌ Unable to fetch market data right now")

    elif fetch_btn:
        st.warning("⚠️ Please enter a stock name")