import streamlit as st
import time
import re
import copy

from graph.workflow import run_workflow


def render_chat_tab(state):

    if run_workflow is None:
        st.error("Workflow not initialized properly")
        return
    print("LOADING TAB1_CHAT")
    # -------------------------------
    # Init
    # -------------------------------
    #state = st.session_state["agent_state"]
    state.setdefault("profile", {})
    state.setdefault("last_intent", None)
    state.setdefault("stage", None)
    state.setdefault("memory", [])

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
            state["memory"]= []
            st.session_state.pending_query = None
            st.rerun()

    # -------------------------------
    # Suggestions (first load)
    # -------------------------------
    if len(state["memory"]) == 0 and not st.session_state.pending_query:

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
                    state["memory"].append({
                                "query": q_sample,
                                "assistant": None
                    })
                    st.session_state.current_index = len(state["memory"]) - 1
                    st.session_state.pending_query = q_sample
                    st.rerun()

    # -------------------------------
    # Chat history
    # -------------------------------
    display_memory = state["memory"][-20:]  # only UI limit

    for i, m in enumerate(display_memory):

        # User
        with st.chat_message("user"):
            st.markdown(m["query"])

        # Assistant
        if m["assistant"] is not None:
            with st.chat_message("assistant"):

                # 🔥 ONLY animate last message
                if not m.get("animated", False):
                    placeholder = st.empty()
                    words = m["assistant"].split(" ")
                    full_text = ""

                    for w in words:
                        full_text += w + " "
                        placeholder.markdown(full_text)
                        time.sleep(0.02)
                    m["animated"] = True   # 👈 ADD THIS LINE
                else:
                    st.markdown(m["assistant"])

                if m.get("agent"):
                    st.caption(f"🧠 {m['agent']}")
                    
                if m.get("trace"):

                    trace_steps = []

                    for t in m["trace"]:

                        if isinstance(t, dict):
                            agent = t.get("agent", "")
                            action = t.get("action", "")

                            if agent:
                                if action:
                                    trace_steps.append(f"{agent} ({action})")
                                else:
                                    trace_steps.append(agent)

                            else:
                                trace_steps.append(str(t))
                        else:
                                trace_steps.append(str(t))

                    if trace_steps:  # 👈 prevents empty output
                        trace_text = " → ".join(trace_steps)
                        st.caption(f"🧠 Flow: {trace_text}")

    if st.session_state.pending_query and state["memory"] and state["memory"][-1]["assistant"] is None:
        with st.chat_message("assistant"):
            st.markdown("🤖 Thinking...")
    # -------------------------------
    # Chat input (NO extra spacing)
    # -------------------------------
    user_input = st.chat_input("Ask your financial question...")

    # -------------------------------
    # New query
    # -------------------------------
    if st.session_state.pending_query:

        q = st.session_state.pending_query  

        memory_snapshot = copy.deepcopy(state["memory"])

        # 🔥 NEW: extract last valid profile from memory
        last_profile = {}

        for m in reversed(state["memory"]):
            p = m.get("profile")


            # ✅ allow profile even if partial
            if p and isinstance(p, dict) and any(v for v in p.values()):
                last_profile = p
                break

        last_stage = None
        for m in reversed(state["memory"]):
            if m.get("stage"):
                last_stage = m["stage"]
                break

        result = run_workflow({
        "query": q,
        "memory": memory_snapshot,
        "profile": last_profile,   # ✅ THIS IS THE FIX
        "stage": last_stage 
        })

        answer = result.get("answer")

        if not answer or not answer.strip():
            answer = result.get("error") or "Something went wrong. Please try again."

        agent = result.get("agent") or "advisor_agent"

        # ✅ ALWAYS update last message
        state["memory"][-1]["assistant"] = answer
        state["memory"][-1]["agent"] = agent
        state["memory"][-1]["animated"] = False
        state["memory"][-1]["trace"] = result.get("trace", [])
        state["memory"][-1]["profile"] = result.get("profile", {})
        state["memory"][-1]["stage"] = result.get("stage")
        
        state.update({
            "profile": result.get("profile", state.get("profile")),
            "stage": result.get("stage"),
            "last_intent": result.get("last_intent", state.get("last_intent")),
            "advisor_allocation": result.get("advisor_allocation"),
            "advisor_insights": result.get("advisor_insights"),
            "advisor_advice": result.get("advisor_advice"),
            "active_asset": result.get("active_asset", state.get("active_asset")),
            })
        st.session_state.pending_query = None
        st.rerun()
        

    if user_input:

        # ALWAYS append fresh user input
        state["memory"].append({
        "query": user_input,
        "assistant": None   # ✅ IMPORTANT
        })

        st.session_state.current_index = len(state["memory"]) - 1
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