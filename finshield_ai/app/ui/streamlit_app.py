import streamlit as st

from app.agents.router import route
from app.utils.file_handler import save_uploaded_file
from rag.ingest import ingest_document

st.set_page_config(
    page_title="FinShield AI",
    page_icon="🏠",
    layout="wide"
)

def load_css():

    with open("app/ui/style.css") as f:

        st.markdown(
            f"<style>{f.read()}</style>",
            unsafe_allow_html=True
        )

load_css()

# -----------------------------------------
# Sidebar
# -----------------------------------------

with st.sidebar:

    st.title("🏠 FinShield AI")

    st.markdown("""
### 🚀 Features

📄 Executive Summary

Generate a concise policy overview.

---

❓ Ask Question

Ask natural language questions.

---

⚠️ Risk Analysis

Identify exclusions and risks.

---

⚖️ Compare Policies

Compare two policies side by side.

---

### 🤖 AI Stack

- Groq
- ChromaDB
- Sentence Transformers
- Streamlit

---

### 💡 Tips

- Upload **one policy** for Q&A, Summary or Risk Analysis.
- Upload **two policies** to compare them.
""")
    st.caption("Version 1.0")
# -----------------------------------------
# Main Page
# -----------------------------------------

st.markdown("""
<div style="
background:linear-gradient(90deg,#1f77b4,#4F8BF9);
padding:25px;
border-radius:15px;
color:white;
">

<h1>🏠 FinShield AI</h1>

<p style="font-size:18px;">
Compare • Summarize • Analyze Insurance Policies with AI
</p>

</div>
""",
unsafe_allow_html=True)

# --------------------------------------------------
# Welcome
# --------------------------------------------------

st.info("""
👋 **Welcome**

Upload one policy for Summary, Q&A or Risk Analysis.

Upload two policies to compare them.
""")


# ============================================
# Two-column Layout
# ============================================

left, right = st.columns([1, 2], gap="large")

# --------------------------------------------
# LEFT COLUMN
# --------------------------------------------

with left:

    st.subheader("⚙️ Analysis")

    analysis_type = st.selectbox(
        "Choose Analysis",
        [
            "❓ Ask Question",
            "📄 Executive Summary",
            "⚠️ Risk Analysis",
            "📘 Explain Clause",
            "⚖️ Compare Policies"
        ]
    )

    analysis_type = (
        analysis_type.replace("❓ ", "")
                     .replace("📄 ", "")
                     .replace("⚠️ ", "")
                     .replace("📘 ", "")
                     .replace("⚖️ ", "")
    )

    if analysis_type == "Ask Question":
        st.caption("💡 Example: What is covered under this policy?")

    elif analysis_type == "Executive Summary":
        st.caption("💡 Generates a structured summary of the uploaded policy.")

    elif analysis_type == "Risk Analysis":
        st.caption("💡 Identifies risks, exclusions and coverage gaps.")

    elif analysis_type == "Compare Policies":
        st.caption("💡 Upload two policies to compare them.")

    elif analysis_type == "Explain Clause":
        st.caption("💡 Paste an insurance clause to get a plain-English explanation.")

    if analysis_type == "Ask Question":
        query = st.text_input("Ask a question")

    elif analysis_type == "Explain Clause":
        query = st.text_area("Paste the clause")

    else:
        query = ""

# --------------------------------------------
# RIGHT COLUMN
# --------------------------------------------

with right:

    with st.container(border=True):

        st.subheader("📂 Upload Policy")

        policy_b = None

        upload_label = (
                "📄 Upload Policy A"
        if analysis_type == "Compare Policies"
        else "📄 Upload Insurance Policy"
        )

        policy_a = st.file_uploader(
            upload_label,
            type=["pdf"],
            key="policy_a"
        )

    if policy_a:
        st.success(f"✅ {policy_a.name}")

    if analysis_type == "Compare Policies":

        policy_b = st.file_uploader(
            "📄 Upload Policy B",
            type=["pdf"],
            key="policy_b"
        )

        st.caption("Supported format: PDF")

        if policy_b:
            st.success(f"✅ {policy_b.name}")

    analyze = st.button(
        "🚀 Analyze Policy",
        use_container_width=True,
        type="primary"
    )

    if analyze:

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

            with st.spinner(
                    "🔍 Reading document...\n\n"
                    "🧠 Retrieving policy context...\n\n"
                    "🤖 Generating AI response..."
                ):
            
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
                    response = route(
                    analysis_type=analysis_type,
                    pdf_path_a=pdf_path_a,
                    pdf_path_b=pdf_path_b
                    )

            st.divider()
            st.markdown("## 📊 Analysis Results")

            # Results
            st.success("✅ Analysis completed successfully.")

            col1, col2 = st.columns(2)

            with col1:
                st.metric(
                    label="📊 Analysis",
                    value=analysis_type
                )

            with col2:
                st.metric(
                    label="🤖 AI Agent",
                    value=response["agent"]
                )


            sources = response["result"].get("sources", [])

            tab1, tab2 = st.tabs(
                ["📄 Results", "📚 Retrieved Context"]
                )

            with tab1:
                st.subheader(f"📄 {analysis_type} Results")

                with st.container(border=True):
                    st.markdown(response["result"]["answer"])
                st.download_button(
                    label="📥 Download Analysis",
                    data=response["result"]["answer"],
                    file_name=f"{analysis_type.lower().replace(' ', '_')}_analysis.txt",
                    mime="text/plain"
                    )

            with tab2:

                if sources:

                    for i, doc in enumerate(sources, start=1):
                        st.markdown(f"### Source {i}")
                        st.write(doc)
                        st.divider()

                else:

                    st.info("No retrieved context available.")

            st.warning(
                    "⚠️ AI-generated insights are based only on the uploaded documents. "
                    "Please review the original policy before making insurance decisions."
            )

        except Exception as e:
            st.error(str(e))



# --------------------------------------------------
# Footer
# --------------------------------------------------

st.divider()

st.caption(
    "🏠 FinShield AI • Version 1.0 • Powered by Groq, ChromaDB, Sentence Transformers & Streamlit"
)

