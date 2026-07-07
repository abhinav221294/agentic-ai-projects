import streamlit as st
from rag.rag_pipeline import ask_question

st.title("FinShield AI")

query = st.text_input("Ask a question")

if st.button("Submit"):

    with st.spinner("Analyzing policy..."):

        result = ask_question(query)

    st.success("Analysis completed")

    st.markdown(result["answer"])

    with st.expander("Sources"):

        for d in result["sources"]:

            st.write(d)