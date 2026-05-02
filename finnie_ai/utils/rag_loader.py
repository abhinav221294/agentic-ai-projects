import streamlit as st
from tools.rag_pipeline import RAGPipeline

@st.cache_resource
def get_rag():
    return RAGPipeline()
rag = get_rag()