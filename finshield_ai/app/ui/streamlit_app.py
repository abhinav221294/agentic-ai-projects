import streamlit as st
from app.agents.router import route

st.set_page_config(
    page_title="FinShield AI",
    page_icon="🏠",
    layout="wide"
)

st.title("🏠 FinShield AI")
st.caption("AI-powered Insurance Policy Intelligence")

# -------------------------
# Upload Policy
# -------------------------

uploaded_policy = st.file_uploader(
    "Upload Insurance Policy",
    type=["pdf"]
)

# -------------------------
# Analysis Type
# -------------------------

analysis_type = st.selectbox(
    "Choose Analysis",
    [
        "Ask Question",
        "Executive Summary",
        "Risk Analysis",
        "Explain Clause"
    ]
)

# -------------------------
# Question
# -------------------------

query = ""

if analysis_type == "Ask Question":
    query = st.text_input("Ask a question")

elif analysis_type == "Explain Clause":
    query = st.text_area("Paste the clause")

# -------------------------
# Analyze
# -------------------------

if st.button("Analyze"):

    if uploaded_policy is None:
        st.warning("Please upload an insurance policy.")
        st.stop()

    if analysis_type in ["Ask Question", "Explain Clause"] and not query.strip():
        st.warning("Please enter a question.")
        st.stop()

    with st.spinner("Analyzing policy..."):

        response = route(query)

    st.success(f"Selected Agent: {response['agent']}")

    st.subheader("Answer")
    st.markdown(response["result"]["answer"])

    with st.expander("Retrieved Context"):

        for i, doc in enumerate(response["result"]["sources"], start=1):
            st.markdown(f"**Source {i}**")
            st.write(doc)
            st.divider()