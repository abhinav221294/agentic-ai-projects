import streamlit as st
from agents.news_agent import news_agent

def render_news_tab(state):

    # 🔥 Wrap EVERYTHING
    st.title("📰 Latest News")

    news_input = st.text_input("Search news (e.g., Tesla, Apple, market)")
    news_btn = st.button("📰 Get News")

    if news_btn and news_input:

        with st.spinner("Fetching latest news..."):
            #state = st.session_state["agent_state"]
            state["query"] = f"{news_input} news"

            result = news_agent(state)
            news_text = result.get("answer", "")

            
            state["stage"] = "news"
            state["last_intent"] = "news"
            
            # Store separately (NOT in chat memory)
            state["news_data"] = news_text
            state["news_query"] = news_input
            
            # 🔥 Better formatting
            for line in news_text.split("\n"):
                if line.strip():
                    st.markdown(line.strip())
