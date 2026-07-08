import streamlit as st
from app.agents.router import route

st.title("🏠 FinShield AI")

query = st.text_input("Ask a question")

if st.button("Submit"):

    if not query.strip():
        st.warning("Please enter a question.")
        st.stop()

    with st.spinner("Analyzing..."):

        response = route(query)

    st.success(f"Selected Agent: {response['agent']}")

    st.subheader("Answer")
    st.markdown(response["result"]["answer"])

    with st.expander("Retrieved Context"):

        for i, doc in enumerate(response["result"]["sources"], start=1):
            st.markdown(f"**Source {i}**")
            st.write(doc)
            st.divider()