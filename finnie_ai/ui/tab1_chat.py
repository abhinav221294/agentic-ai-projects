import streamlit as st
from graph.workflow import run_workflow
import time
import re

def render_chat_tab():

    # -------------------------------
    # Init
    # -------------------------------
    if "memory" not in st.session_state:
        st.session_state.memory = []

    if "pending_query" not in st.session_state:
        st.session_state.pending_query = None
        st.session_state.current_index = None
    # -------------------------------
    # Header
    # -------------------------------
    col1, col2 = st.columns([10, 1], vertical_alignment="center")

    with col1:
        st.markdown("""
        <h2 style='margin-bottom:2px;'>💬 Assistant</h2>
        <p style='color:gray; margin-top:0;'>Ask anything about finance, stocks, or investing</p>
        """, unsafe_allow_html=True)

    with col2:
        if st.button("🧹"):
            st.session_state.memory = []
            st.session_state.pending_query = None
            st.rerun()

    # -------------------------------
    # Suggestions (first load)
    # -------------------------------
    if len(st.session_state.memory) == 0 and not st.session_state.pending_query:

        st.markdown("### 🧪 Try these:")

        sample_queries = [
            "What is SIP?",
            "Is crypto risky?",
            "Where should I invest money?",
            "Tesla stock price?",
            "Explain mutual funds"
        ]

        cols = st.columns(3)

        for i, q_sample in enumerate(sample_queries):
            with cols[i % 3]:
                if st.button(q_sample, use_container_width=True):
                    st.session_state.memory.append({
                                "user": q_sample,
                                "assistant": None
                    })
                    st.session_state.current_index = len(st.session_state.memory) - 1
                    st.session_state.pending_query = q_sample
                    st.rerun()
    # -------------------------------
    # New query
    # -------------------------------
    if st.session_state.pending_query:

            q = st.session_state.pending_query
            with st.spinner("🤖 Thinking..."):
                memory_snapshot = st.session_state.memory.copy()

                result = run_workflow({
                    "query": q,
                    "memory": memory_snapshot
                })

            answer = result.get("answer") #or "Something went wrong."
            if not answer or not answer.strip():
                    answer = """I had trouble generating a response.

Here’s a simple starting point:

Recommendation  
70% Balanced Advantage Fund  
30% Short-term Debt Fund  

This is a safe, low-risk allocation.

You can refine this by sharing your goal and investment type."""
                    
            agent = result.get("agent") or "advisor_agent"
            data = result.get("data")

            # update memory
            idx = st.session_state.get("current_index")

            if isinstance(idx, int) and 0 <= idx < len(st.session_state.memory):
                st.session_state.memory[idx]["assistant"] = answer
                st.session_state.memory[idx]["agent"] = agent
                st.session_state.memory[idx]["animated"] = False  # 👈 add

            st.session_state.pending_query = None
            st.session_state.current_index = None
            st.rerun()
    # -------------------------------
    # Chat history
    # -------------------------------
    display_memory = st.session_state.memory[-20:]  # only UI limit

    for i, m in enumerate(display_memory):

        # User
        with st.chat_message("user"):
            st.write(m["user"])

        # Assistant
        if m["assistant"] is not None:
            with st.chat_message("assistant"):

                # 🔥 ONLY animate last message
                if not m.get("animated", False):
                    placeholder = st.empty()
                    full_text = ""

                    for char in m["assistant"]:
                        full_text += char
                        placeholder.markdown(full_text)
                        time.sleep(0.002)
                    m["animated"] = True   # 👈 ADD THIS LINE
                else:
                    st.write(m["assistant"])

                if m.get("agent"):
                    st.caption(f"🧠 {m['agent']}")
    # -------------------------------
    # Chat input (NO extra spacing)
    # -------------------------------
    user_input = st.chat_input("Ask your financial question...")

    if user_input:

        # 🔥 Immediately append to memory
        st.session_state.memory.append({
            "user": user_input,
            "assistant": None
        })

        st.session_state.current_index = len(st.session_state.memory) - 1
        st.session_state.pending_query = user_input
        st.rerun()

    
                
    st.markdown(
    """
    <script>
        var body = window.parent.document.querySelector(".main");
        body.scrollTo({top: body.scrollHeight, behavior: 'smooth'});
    </script>
    """,
    unsafe_allow_html=True
)