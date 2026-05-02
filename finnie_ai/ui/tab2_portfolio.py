import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import time
from tools.summarize_portfolio import analyze_portfolio
from utils.price_utils import get_price
from utils.fx_currency import get_usd_to_inr
from utils.stock_mapper import normalize_stock
import json

ASSET_RISK_MAP = {
    "Stock": 0.8,
    "ETF": 0.6,
    "Mutual Fund": 0.5,
    "SIP": 0.4,
    "Bonds": 0.2, 
    "Crypto": 1.0
}

def set_mode_amount():
    st.session_state["mode_input"] = "Amount"

def set_mode_quantity():
    st.session_state["mode_input"] = "Quantity"


def render_portfolio_tab(state):

    st.title("📊 Portfolio Insights")

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        Company = st.text_input("Company", key="company_input")

    with col2:
        mode = st.selectbox("Mode", ["Quantity", "Amount"], key="mode_input")

    with col3:
        quantity = st.number_input(
            "Quantity",
            min_value=1.0,
            step=1.0,
            key="qty_input",
            disabled=(mode == "Amount"),
            on_change=set_mode_quantity
        )

    with col4:
        amount = st.number_input(
            "Amount (₹)",
            min_value=1.0,
            step=100.0,
            key="amt_input",
            disabled=(mode == "Quantity"),
            on_change=set_mode_amount
        )

    with col5:
        #risk = st.selectbox("Risk Level", ["Low", "Medium", "High"], key="risk_input")
        asset_type = st.selectbox(
                        "Asset Type",
                        ["Stock", "ETF", "Mutual Fund", "Crypto", "SIP", "Bonds"],
                        key="asset_type_input"
                        )

    #  Live preview
    if Company:
        normalized_Company = normalize_stock(Company)
        price = get_price(normalized_Company)

        if price:
            usd_to_inr = get_usd_to_inr()
            price_inr = price if normalized_Company.endswith(".NS") else price * usd_to_inr

            st.caption(f"Current Price: ₹ {round(price_inr, 2)}")


            if mode == "Quantity" and quantity:
                st.caption(f"💰 Value: ₹ {round(quantity * price_inr, 2)}")

            elif mode == "Amount" and amount:
                st.caption(f"📊 Qty: {round(amount / price_inr, 2)}")

    #  Button (no form)
    add_btn = st.button("Add to Portfolio")

    #state = st.session_state["agent_state"]
    state.setdefault("portfolio", [])

    if add_btn and Company.strip():
        normalized_Company = normalize_stock(Company)     
        price = get_price(normalized_Company)

        if not price:
                st.error("Price not available")
        else:
                usd_to_inr = get_usd_to_inr()
                price_inr = price if normalized_Company.endswith(".NS") else price * usd_to_inr

                if mode == "Quantity":
                    if quantity <= 0:
                        st.error("Enter valid quantity")  
                        return 
                    final_qty = quantity
                    final_amt = quantity*price_inr
                else:
                    if amount <= 0:
                        st.error("Enter valid amount")
                        return
                    final_amt = amount
                    final_qty = amount/price_inr

                found = False

                for p in state["portfolio"]:
                    if p["Company"] == normalized_Company and p["asset_type"] == asset_type:
                        p["quantity"] += round(final_qty, 2)
                        p["amount"] += round(final_amt, 2)
                        found = True
                        break

                if not found:
                    state["portfolio"].append({
                    "Company": normalized_Company,
                    "quantity": round(final_qty, 2),
                    "amount": round(final_amt, 2),
                    "asset_type":asset_type
                    #"risk": risk
                    })
                st.success(f"{normalized_Company} updated in portfolio")
                
                # Reset inputs
                state["reset_form"] = True
                st.rerun()

    st.markdown("### 📁 Your Portfolio")

    portfolio = state["portfolio"]

    if not portfolio:
        st.info("No holdings added yet.")
    else:
        total_value = 0
        price_cache = {}
        usd_to_inr = get_usd_to_inr()

        rows = []
        errors = []

        for item in portfolio:
            symbol = item["Company"]
            qty = item["quantity"]
            #amt = item.get("amount", 0)
            #risk = item.get("risk", "Unknown")
            asset_type=item.get("asset_type","Unknown")

            if symbol not in price_cache:
                price_cache[symbol] = get_price(symbol)

            price = price_cache[symbol]

            if not price:
                errors.append(symbol)

            if price:
                price_inr = price if symbol.endswith(".NS") else price * usd_to_inr
                if price_inr == 0:
                    st.error("Invalid price")
                    return
                value = price_inr * qty

                rows.append({
                    "Company": symbol,
                    "Quantity": qty,
                    "Price (₹)": round(price_inr, 2),
                    "Value (₹)": round(value, 2),
                    "asset_type":asset_type
                    #"Risk": risk
                })

                total_value += value
        #st.write(st.session_state["portfolio"])
        if errors:
            placeholder = st.empty()
            placeholder.warning(f"Missing price: {', '.join(errors)}")
            time.sleep(2)
            placeholder.empty()

        df = pd.DataFrame(rows)

        if not df.empty:
            # 🔹 Sort once (global)
            df = df.sort_values(
                    by=["Company", "asset_type", "Value (₹)"],
                    ascending=[True, True, False]
                    ).reset_index(drop=True)
            
            df = df.reset_index(drop=True)
            

            df["Allocation (%)"] = (df["Value (₹)"] / total_value) * 100
            df["Allocation (%)"] = df["Allocation (%)"].round(2)

            # 🔹 Table
            st.dataframe(df)

            df["Risk Score"] = df["asset_type"].map(ASSET_RISK_MAP)
            df["Weighted Risk"] = df["Risk Score"] * df["Value (₹)"]

            portfolio_risk = df["Weighted Risk"].sum() / total_value

            asset_type_summary = df.groupby("asset_type")["Value (₹)"].sum().to_dict()

            state.update({
            "portfolio_summary": {
            "total_value": total_value,
            "risk_score": round(portfolio_risk, 2),
            "diversification": len(df)
            },
            "portfolio_allocation": df[["Company", "Allocation (%)"]].to_dict("records"),
            "portfolio_assets": asset_type_summary
            })

            # 🔹 KPI Cards (Top section)
            top_company = df.loc[df['Value (₹)'].idxmax(), 'Company']
            diversification = len(df)

            k1, k2, k3 = st.columns(3)
            k1.metric("💰 Total Value", f"₹ {round(total_value, 2)}")
            k2.metric("🏆 Top Holding", top_company)
            k3.metric("📊 Diversification", diversification)

            # 🔹 Charts Section
            st.markdown("## 📊 Portfolio Visualizations")

            if len(df) == 1:
                st.info("Add more companies to see distribution")
            else:
                # Create combined label (Company + Asset Type)
                df["Label"] = df["Company"] + " (" + df["asset_type"] + ")"

                # 🔹 Group data
                asset_df = df.groupby("asset_type")["Value (₹)"].sum()
                quantity_df = df.groupby("Company")["Quantity"].sum()

                # 🔹 Layout
                c1, c2 = st.columns(2)
                c3, c4 = st.columns(2)

                # -------------------------------
                # 🔸 1. Portfolio Distribution (Pie)
                # -------------------------------
                with c1:
                    st.subheader("Portfolio Distribution")

                    fig1, ax1 = plt.subplots(figsize=(4, 4))
                    ax1.pie(
                    df["Value (₹)"],
                        labels=df["Company"],
                        autopct="%1.1f%%",
                        startangle=90,
                        wedgeprops={'edgecolor': 'white'}
                    )
                    ax1.axis('equal')

                    st.pyplot(fig1)

                # -------------------------------
                # 🔸 2. Value by Company (Bar)
                # -------------------------------
                with c2:
                    st.subheader("Asset Allocation")

                    fig2, ax2 = plt.subplots(figsize=(4, 4))
                    ax2.pie(
                    asset_df,
                        labels=asset_df.index,
                        autopct="%1.1f%%",
                        startangle=90,
                        wedgeprops={'edgecolor': 'white'}
                    )
                    ax2.axis('equal')

                    st.pyplot(fig2)
                    

                # -------------------------------
                # 🔸 3. Asset Type Distribution
                # -------------------------------
                with c3:
                    st.subheader("Value by Company")

                    fig3, ax3 = plt.subplots(figsize=(4, 4))
                    ax3.bar(df["Company"], df["Value (₹)"])

                    ax3.set_ylabel("Value (₹)")
                    ax3.set_xlabel("")

                    st.pyplot(fig3)

                # -------------------------------
                # 🔸 4. Top Holdings (Horizontal)
                # -------------------------------
                with c4:
                        st.subheader("Top Holdings")

                        top_df = df.sort_values(by="Value (₹)", ascending=True)

                        fig4, ax4 = plt.subplots(figsize=(4, 4))
                        ax4.barh(top_df["Label"], top_df["Value (₹)"])

                        ax4.set_xlabel("Value (₹)")

                        st.pyplot(fig4)

                # -------------------------------
                # 🔸 5. Quantity by Company (Full Width)
                # -------------------------------
                st.subheader("Quantity by Company")

                fig5, ax5 = plt.subplots(figsize=(6, 4))
                ax5.bar(quantity_df.index, quantity_df.values)

                ax5.set_ylabel("Quantity")
                ax5.set_xlabel("")

                st.pyplot(fig5)
            
            if portfolio_risk > 0.7:
                st.metric("📉 Risk Score", round(portfolio_risk, 2), "High 🔴")
            elif portfolio_risk > 0.4:
                st.metric("📉 Risk Score", round(portfolio_risk, 2), "Medium 🟡")
            else:
                st.metric("📉 Risk Score", round(portfolio_risk, 2), "Low 🟢")

            holdings_text = df[['Company','Value (₹)','asset_type','Allocation (%)']].to_string(index=False)
            
            
            

            asset_df = df.groupby("asset_type")["Value (₹)"].sum()

            top_asset = asset_df.idxmax()
            st.info(f"📌 Highest allocation in {top_asset}")
                
            if st.button("Analyze Portfolio"):
                with st.spinner("Analyzing portfolio..."):
                        payload = {
                                "total_value": total_value,
                                "holdings": holdings_text,
                                "risk_distribution": asset_type_summary
                        }

                        result = analyze_portfolio(payload)
                        state["portfolio_insights"] = result

                        st.subheader("📊 AI Insights")
                        st.write(result)