"""
Embedding model initialization and configuration.
"""
import streamlit as st
from langchain.embeddings import HuggingFaceEmbeddings
from config.settings import EMBEDDING_MODEL_NAME, EMBEDDING_DEVICE


def get_embedding_model():
    """Initialize and return the embedding model (cached in session state)."""
    if "embedding_model" not in st.session_state:
        st.session_state["embedding_model"] = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL_NAME,
            model_kwargs={'device': EMBEDDING_DEVICE}
        )
    return st.session_state["embedding_model"]

