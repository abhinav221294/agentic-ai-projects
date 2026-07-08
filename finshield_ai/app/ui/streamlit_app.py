import streamlit as st
from app.agents.router import route
from app.utils.file_handler import save_uploaded_file
from rag.ingest import ingest_document

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

    try:
        with st.spinner("📄 Processing document and generating response..."):

            pdf_path = save_uploaded_file(uploaded_policy)

            ingest_document(pdf_path)

            response = route(
            analysis_type,
            query,
            pdf_path
            )

        st.success(f"🤖 Agent Used: {response['agent']}")

        st.subheader("Answer")
        st.markdown(response["result"]["answer"])

        sources = response["result"].get("sources", [])

        if sources:
            with st.expander("Retrieved Context"):
                for i, doc in enumerate(sources, start=1):
                    st.markdown(f"**Source {i}**")
                    st.write(doc)
                    st.divider()

        # -----------------------------------
        # Footer
        # -----------------------------------

        st.divider()

        st.caption(
        "🏠 FinShield AI | AI-Powered Insurance Policy Intelligence | "
        "Groq • ChromaDB • Sentence Transformers • Streamlit"
        )   

    except Exception as e:
        st.error(f"An error occurred: {e}")