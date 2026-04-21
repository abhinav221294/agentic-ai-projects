import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import time

from agents.market_agent import get_finnhub_price
from utils.fx_currency import get_usd_to_inr
from utils.stock_mapper import normalize_stock

def render_portfolio_tab():

    st.title("📊 Portfolio Insights")

    col1, col2 = st.columns(2)

    with col1:
        stock = st.text_input("Stock")

    with col2:
        quantity = st.number_input("Quantity", min_value=1, step=1)

    add_btn = st.button("Add to Portfolio")

    if "portfolio" not in st.session_state:
        st.session_state["portfolio"] = []

    if add_btn and stock.strip():
        normalized_stock = normalize_stock(stock)
        existing = [p["stock"] for p in st.session_state["portfolio"]]

        if normalized_stock not in existing:
            st.session_state["portfolio"].append({
                "stock": normalized_stock,
                "quantity": quantity
            })
        else:
            st.warning("Stock already exists")

    st.markdown("### 📁 Your Portfolio")

    portfolio = st.session_state["portfolio"]

    if not portfolio:
        st.info("No holdings added yet.")
    else:
        total_value = 0
        price_cache = {}
        usd_to_inr = get_usd_to_inr()

        rows = []
        errors = []

        for item in portfolio:
            symbol = item["stock"]
            qty = item["quantity"]

            if symbol not in price_cache:
                price_cache[symbol] = get_finnhub_price(symbol)

            price = price_cache[symbol]

            if not price:
                errors.append(symbol)

            if price:
                price_inr = price if symbol.endswith(".NS") else price * usd_to_inr
                value = price_inr * qty

                rows.append({
                    "Stock": symbol,
                    "Quantity": qty,
                    "Price (₹)": round(price_inr, 2),
                    "Value (₹)": round(value, 2)
                })

                total_value += value

        if errors:
            placeholder = st.empty()
            placeholder.warning(f"Missing price: {', '.join(errors)}")
            time.sleep(2)
            placeholder.empty()

        df = pd.DataFrame(rows)

        if not df.empty:
            # 🔹 Sort once (global)
            df = df.sort_values(by="Value (₹)", ascending=False)

            # 🔹 Table
            st.dataframe(df)

            # 🔹 KPI Cards (Top section)
            top_stock = df.loc[df['Value (₹)'].idxmax(), 'Stock']
            avg_value = df['Value (₹)'].mean()

            k1, k2, k3 = st.columns(3)
            k1.metric("💰 Total Value", f"₹ {round(total_value, 2)}")
            k2.metric("🏆 Top Holding", top_stock)
            k3.metric("📊 Avg Value", f"₹ {round(avg_value, 2)}")

            # 🔹 Charts Section
            col_left, col_right = st.columns(2)

            if len(df) == 1:
                st.info("Add more stocks to see distribution")
            else:
                # 🔸 Pie Chart
                with col_left:
                    st.subheader("Portfolio Distribution")

                    fig, ax = plt.subplots(figsize=(4, 4))
                    ax.pie(
                        df['Value (₹)'],
                        labels=df['Stock'],
                        autopct="%1.1f%%",
                        startangle=90,
                        wedgeprops={'edgecolor': 'white'}
                    )
                    ax.axis('equal')
                    st.pyplot(fig, use_container_width=False)

                # 🔸 Bar Chart
                with col_right:
                    st.subheader("Value by Stock")
                    fig2, ax2 = plt.subplots(figsize=(4, 4))
                    ax2.bar(df['Stock'], df['Value (₹)'])
                    ax2.set_xlabel("Stock")
                    ax2.set_ylabel("Value (₹)")
                    st.pyplot(fig2, use_container_width=False)