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

# --------------------------------------------------
# Upload Policies
# --------------------------------------------------

policy_a = st.file_uploader(
    "Upload Policy A",
    type=["pdf"],
    key="policy_a"
)

policy_b = st.file_uploader(
    "Upload Policy B (Only for Compare Policies)",
    type=["pdf"],
    key="policy_b"
)

# --------------------------------------------------
# Analysis
# --------------------------------------------------

analysis_type = st.selectbox(
    "Choose Analysis",
    [
        "Ask Question",
        "Executive Summary",
        "Risk Analysis",
        "Explain Clause",
        "Compare Policies"
    ]
)

# --------------------------------------------------
# User Input
# --------------------------------------------------

query = ""

if analysis_type == "Ask Question":
    query = st.text_input("Ask a question")

elif analysis_type == "Explain Clause":
    query = st.text_area("Paste the clause")

# --------------------------------------------------
# Analyze
# --------------------------------------------------

if st.button("Analyze"):

    if policy_a is None:
        st.warning("Please upload Policy A.")
        st.stop()

    if analysis_type in ["Ask Question", "Explain Clause"] and not query.strip():
        st.warning("Please enter a question.")
        st.stop()

    if analysis_type == "Compare Policies" and policy_b is None:
        st.warning("Please upload Policy B.")
        st.stop()

    try:

        with st.spinner("📄 Processing..."):

            pdf_path_a = save_uploaded_file(policy_a)

            # Existing functionality
            if analysis_type != "Compare Policies":

                ingest_document(pdf_path_a)

                response = route(
                    analysis_type=analysis_type,
                    query=query,
                    pdf_path=pdf_path_a
                )

            # Placeholder for comparison
            else:

                pdf_path_b = save_uploaded_file(policy_b)

                st.info("🚧 Compare Policies will be implemented next.")

                st.stop()

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

    except Exception as e:

        st.error(str(e))

# --------------------------------------------------
# Footer
# --------------------------------------------------

st.divider()

st.caption(
    "🏠 FinShield AI | AI-Powered Insurance Policy Intelligence | "
    "Groq • ChromaDB • Sentence Transformers • Streamlit"
)