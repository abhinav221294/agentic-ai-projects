import streamlit as st

st.title("FinShield AI")

pdf = st.file_uploader(
    "Upload Policy Document",
    type=["pdf"]
)

question = st.text_input(
    "Ask a question"
)

if st.button("Submit"):

    st.success("Pipeline coming tomorrow")