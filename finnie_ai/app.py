import streamlit as st
from ui.tab1_chat import render_chat_tab
from ui.tab2_portfolio import render_portfolio_tab
from ui.tab3_market import render_market_tab
from ui.tab4_news import render_news_tab

st.set_page_config(page_title="Finnie AI", layout="wide")

# -------------------------------
# GLOBAL CSS (FINAL CLEAN)
# -------------------------------
st.markdown("""
<style>

/* Tabs */
button[data-baseweb="tab"] {
    font-size: 16px;
    padding: 10px 20px;
    border-radius: 8px;
}
button[data-baseweb="tab"][aria-selected="true"] {
    background-color: #1d4ed8;
    color: white;
}

/* Layout */
.block-container {
    padding-top: 1rem;
    padding-bottom: 0.5rem;
    padding-left: 2rem;
    padding-right: 2rem;
}

/* Center tabs */
section[data-testid="stTabs"] {
    max-width: 800px;
    margin: 0 auto 0.5rem auto;
}

/* Vertical spacing */
div[data-testid="stVerticalBlock"] > div {
    gap: 0.75rem;
}

/* Chat container */
.chat-container {
    max-width: 800px;
    margin: auto;
}

/* 🔥 Sticky Chat Input (FINAL FIX) */
div[data-testid="stChatInput"] {
    position: sticky;
    bottom: 0;
    display: flex;
    justify-content: center;
    padding: 16px 0;
    background: transparent;
    z-index: 10;
}

/* Add a subtle gradient instead of hard bar */
div[data-testid="stChatInput"]::before {
    content: "";
    position: absolute;
    left: 0;
    right: 0;
    bottom: 0;
    height: 80px;
    background: linear-gradient(to top, rgba(0,0,0,0.35), transparent);
    z-index: -1;
}

/* Input width */
div[data-testid="stChatInput"] > div {
    max-width: 800px;
    width: 100%;
    backdrop-filter: blur(6px);
}

/* Input styling */
div[data-testid="stChatInput"] textarea {
    border-radius: 14px;
    padding: 12px;
    background: rgba(255,255,255,0.04);
}

/* Focus */
div[data-testid="stChatInput"] textarea:focus {
    outline: none;
    border: 1px solid rgba(59,130,246,0.6);
    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
}

/* Button hover */
button {
    transition: all 0.15s ease;
}
button:hover {
    transform: translateY(-1px);
    opacity: 0.95;
}

</style>
""", unsafe_allow_html=True)

# -------------------------------
# HEADER
# -------------------------------
st.markdown("""
<div style="padding-left:2rem;">
    <h1 style='margin-bottom:4px;'>🤖 Finnie AI</h1>
    <p style='color:gray; margin-top:0; font-size:14px;'>AI-powered financial assistant</p>
</div>
""", unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

# -------------------------------
# TABS
# -------------------------------
tab1, tab2, tab3, tab4 = st.tabs(
    ["💬 Chat", "📊 Portfolio", "📈 Market Trends", "News 📰"]
)

with tab1:
    render_chat_tab()

with tab2:
    render_portfolio_tab()

with tab3:
    render_market_tab()

with tab4:
    render_news_tab()