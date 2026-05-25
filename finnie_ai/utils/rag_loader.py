import streamlit as st
from tools.rag_pipeline import RAGPipeline

@st.cache_resource
def get_rag():
    return RAGPipeline()

rag = None

def get_rag_instance():
    global rag
    if rag is None:
        rag = RAGPipeline()
    return rag