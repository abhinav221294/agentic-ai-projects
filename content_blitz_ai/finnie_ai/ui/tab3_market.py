import streamlit as st
import yfinance as yf
from utils.llm import get_llm
from utils.prompts import MARKET_ANALYSIS_PROMPT
from utils.stock_mapper import normalize_stock
from utils.price_utils import get_price

def render_market_tab(state):
    #state = st.session_state["agent_state"] 
    
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
                
                currency = "₹" if symbol.endswith(".NS") else "$"
                display_name = symbol.replace(".NS", "")
                # ✅ ADD THIS BLOCK HERE
                if len(data) < 2:
                    latest = data["Close"].iloc[-1]

                    st.subheader(f"{display_name} Price Trend (Last 1 Month)")
                    st.caption(f"Prices shown in {currency}")

                    st.line_chart(data["Close"], use_container_width=True)

                    st.metric(
                            label=f"{display_name} Price",
                            value=f"{round(latest,2):,.2f}"
                        )

                    st.warning("⚠️ Not enough data to calculate trend")
                    return


                # -------------------------
                # EXISTING CHART
                # -------------------------
                st.line_chart(data["Close"], use_container_width=True)

                latest = data["Close"].iloc[-1]
                prev_day = data["Close"].iloc[-2]

                change = latest - prev_day
                percent_change = (change / prev_day) * 100
                
                memory = state.setdefault("memory", [])

                price_text = round(latest, 2) if latest is not None else "N/A"

                if not memory or memory[-1].get("query") != stock_input:
                    memory.append({
                    "query": stock_input,
                    "assistant": f"{symbol} price is {price_text}",
                    "agent": "market_tab",
                    "stage": "market"
                    })
                
                state.update({
                "market_symbol": symbol,
                "market_price": round(latest, 2),
                "market_change": round(change, 2),
                "market_change_pct": round(percent_change, 2),
                "market_trend": "up" if change > 0 else "down"
                })

                state["last_intent"] = "market"
                state["stage"] = "market"

                high_price = data["High"].max()
                low_price = data["Low"].min()
                range_pct = ((high_price - low_price) / low_price) * 100
                
                display_name = symbol.replace(".NS", "")
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric(
                        label=f"{display_name} Price",
                        value=round(latest, 2),
                        delta=f"{round(change,2)} ({round(percent_change,2)}%)"  # ✅ FIX: proper formatting
                    )

                with col2:
                    st.metric(
                        label="📈 Highest (1 Month)",
                        value=round(high_price, 2)
                    )

                with col3:
                    st.metric(
                        label="📉 Lowest (1 Month)",
                        value=round(low_price, 2)
                    )

                if change > 0:
                    st.success("📈 Stock is UP compared to yesterday")
                else:
                    st.warning("📉 Stock is down compared to yesterday")

                st.caption("📊 Based on last 1 month data")

                # Trend classification
                if abs(percent_change) < 1:
                    trend = "➡️ Sideways"
                elif percent_change > 0:
                    trend = "📈 Uptrend"
                else:
                    trend = "📉 Downtrend"
                    
                # Risk logic (simple version)
                symbol_lower = symbol.lower()

                if any(x in symbol_lower for x in ["tcs", "infy", "reliance"]):
                    risk = "Medium ⚖️"
                else:
                    risk = "Medium to High ⚠️"

                # UI display
                st.markdown("### 🧠 Market Insight")

                # 3-column summary (cleaner than one long line)
                c1, c2, c3 = st.columns(3)

                with c1:
                    st.metric("Trend", trend)

                with c2:
                    st.metric("1 Month Range", f"{range_pct:.2f}%")

                with c3:
                    st.metric("Risk", risk)
                
                context = f"""
                Stock: {display_name}
                Trend: {trend}
                1M Range: {range_pct}
                Risk: {risk}
                """
                
                prompt = MARKET_ANALYSIS_PROMPT.format(context)
                            
                llm = get_llm(temperature=0.1,max_tokens=250)
                try:
                    response = llm.invoke(prompt)
                    suggestion = (response.content or "").strip()

                    if not suggestion:
                        suggestion = "Analysis not available right now. Please try again."

                except Exception:
                        suggestion = "Unable to generate insight at the moment."
                
                # Actionable note
                st.info(f"💡 **What to do:** {suggestion}")

            except Exception:
                current_price = get_price(symbol)
                memory = state.setdefault("memory", [])

                price_text = round(current_price, 2) if current_price is not None else "N/A"

                if not memory or memory[-1].get("query") != stock_input:
                    memory.append({
                    "query": stock_input,
                    "assistant": f"{symbol} price is {price_text}",
                    "agent": "market_tab",
                    "stage": "market"
                    })

                if current_price is not None:
                    state.update({
                    "market_symbol": symbol,
                    "market_price": round(current_price, 2),
                    "market_trend": "unknown",
                    "market_source": "fallback"
                    })
                    st.warning("⚠️ Showing live price (chart unavailable)")
                    state["stage"] = "market"

                    # -------------------------
                    # ✅ FIX 2: Restore 3-column layout
                    # -------------------------
                    col1, col2, col3 = st.columns(3)

                    with col1:
                            st.metric(
                                label=f"{symbol} Price",
                                value=round(current_price, 2),
                            )

                    with col2:
                            st.metric(
                                label="📊 Data Source",
                                value="Cached API"
                            )

                    with col3:
                        
                            st.metric(
                                label="Trend",
                                value="Live"
                            )

                    # -------------------------
                    # ✅ FIX 4: Restore caption
                    # -------------------------
                    st.caption("⚠️ Chart data unavailable, showing real-time price only")

                else:
                    st.error("❌ Unable to fetch market data right now")

    elif fetch_btn:
        st.warning("⚠️ Please enter a stock name")