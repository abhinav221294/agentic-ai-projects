import streamlit as st
from agents.news_agent import news_agent

def render_news_tab(state):

    st.title("📰 Latest News")

    news_input = st.text_input("Search news (e.g., Tesla, Apple, market)")
    news_btn = st.button("📰 Get News")

    output_placeholder = st.empty()

    if news_btn and news_input:
        output_placeholder.empty()

        # ✅ clear old data (important)
        state.pop("news_articles", None)
        state.pop("news_summary", None)

        with st.spinner("Fetching latest news..."):
            state["query"] = f"{news_input} news"

            result = news_agent(state)
            news_text = result.get("answer", "")

            state["stage"] = "news"
            state["last_intent"] = "news"
            state["news_data"] = news_text
            state["news_query"] = state["query"]

        # ✅ SIMPLE RENDER (like old UI)
        with output_placeholder.container():
            for line in news_text.split("\n"):
                if line.strip():
                    st.markdown(line.strip())