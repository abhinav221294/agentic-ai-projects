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

    # -------------------------------
    # Header
    # -------------------------------
    col1, col2 = st.columns([10, 1], vertical_alignment="center")

    with col1:
        st.markdown("""
        <h3 style='margin-bottom:2px;'>💬 Assistant</h3>
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
                    st.session_state.pending_query = q_sample
                    st.rerun()

    # -------------------------------
    # Chat history
    # -------------------------------
    for m in st.session_state.memory:

        # User message
        with st.chat_message("user"):
            st.write(m["user"])

        # Assistant message (ONLY if exists)
        if m["assistant"] is not None:
            with st.chat_message("assistant"):
                st.write(m["assistant"])

                if m.get("agent"):
                    st.caption(f"🧠 {m['agent']}")
                
    # -------------------------------
    # New query
    # -------------------------------
    if st.session_state.pending_query:

        q = st.session_state.pending_query

        with st.chat_message("assistant"):
            with st.spinner("🤖 Thinking..."):
                result = run_workflow({
                    "query": q,
                    "memory": st.session_state.memory
            })

            answer = result.get("answer", "No response")
            answer = answer.replace(". ", ".\n\n")
            answer = re.sub(r'(\d+)\.\s*\n\s*', r'\1. ', answer)
            answer = re.sub(r'(Suggested Options:\s*)(\d+)\.\s*\n', r'\1\2. ', answer)

            placeholder = st.empty()
            full_text = ""

            for char in answer:
                full_text += char
                placeholder.markdown(full_text)
                time.sleep(0.005)

            if result.get("agent"):
                st.caption(f"🧠 {result['agent']}")

        st.session_state.memory.append({
            "user": q,
            "assistant": answer,
            "agent": result.get("agent", "Unknown")
        })

        st.session_state.memory = st.session_state.memory[-5:]
        st.session_state.pending_query = None

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

        st.session_state.pending_query = user_input
        st.rerun()