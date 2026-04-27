import streamlit as st
from ui.tab1_chat import render_chat_tab
from ui.tab2_portfolio import render_portfolio_tab
from ui.tab3_market import render_market_tab
from ui.tab4_news import render_news_tab
from dotenv import load_dotenv
import os

load_dotenv()

os.environ["ANONYMIZED_TELEMETRY"] = "False"

st.set_page_config(page_title="Finnie AI", layout="wide")

# -------------------------
# ENV VALIDATION (startup)
# -------------------------
REQUIRED_KEYS = [
    "OPENAI_API_KEY",
    "FINNHUB_API_KEY",
    "TAVILY_API_KEY"
]

missing = [key for key in REQUIRED_KEYS if not os.getenv(key)]

if missing:
    raise ValueError(f"❌ Missing required env variables: {', '.join(missing)}")


# -------------------------------
# 🔐 AUTH CONFIG
# -------------------------------

def load_users():
    raw = os.getenv("APP_USERS", "")
    users = {}

    for pair in raw.split(","):
        if ":" in pair:
            username, password = pair.split(":")
            users[username.strip()] = password.strip()

    return users

VALID_USERS = load_users()


def load_api_keys():
    raw = os.getenv("API_KEYS", "")
    return set(k.strip() for k in raw.split(","))

VALID_KEYS = load_api_keys()

# -------------------------------
# 🔐 LOGIN FUNCTION
# -------------------------------
def login():
    st.markdown("<h2 style='text-align:center;'>🔐 Login to Finnie AI</h2>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1,2,1])

    with col2:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login", use_container_width=True):
            if username in VALID_USERS and VALID_USERS[username] == password:
                st.session_state["authenticated"] = True
                st.session_state["user"] = username
                st.success("Login successful")
                st.rerun()
            else:
                st.error("Invalid credentials")

# -------------------------------
# 🔐 SESSION INIT
# -------------------------------
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

# -------------------------------
# 🔐 BLOCK UNAUTHORIZED USERS
# -------------------------------
if not st.session_state["authenticated"]:
    login()
    st.stop()

# -------------------------------
# 🔑 OPTIONAL API KEY CHECK
# -------------------------------
#api_key = st.text_input("Enter API Key", type="password")

#if api_key not in VALID_KEYS:
#    st.warning("Invalid API Key")
#    st.stop()

# -------------------------------
# GLOBAL CSS (UNCHANGED)
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

/* Sticky Chat Input */
div[data-testid="stChatInput"] {
    position: sticky;
    bottom: 0;
    display: flex;
    justify-content: center;
    padding: 16px 0;
    background: transparent;
    z-index: 10;
}

/* Gradient */
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
st.markdown(f"""
<div style="padding-left:2rem;">
    <h1 style='margin-bottom:4px;'>🤖 Finnie AI</h1>
    <p style='color:gray; margin-top:0; font-size:14px;'>AI-powered financial assistant</p>
    <p style='font-size:12px;'>👤 Logged in as: <b>{st.session_state['user']}</b></p>
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