"""
Session state management utilities.
"""
import streamlit as st


def initialize_session_state():
    """Initialize session state variables."""
    if "search_done" not in st.session_state:
        st.session_state["search_done"] = False
    if "history" not in st.session_state:
        st.session_state["history"] = []
    if "custom_products" not in st.session_state:
        st.session_state["custom_products"] = []
    if "technicien_chat_history" not in st.session_state:
        st.session_state["technicien_chat_history"] = []


def reset_search():
    """Reset search state."""
    st.session_state["search_done"] = False
    st.session_state["history"] = []


def add_custom_product(product_code: str):
    """Add custom product to the list."""
    if product_code.strip():
        if product_code not in st.session_state["custom_products"]:
            st.session_state["custom_products"].append(product_code)
            st.success(f"Added product code: {product_code}")
        else:
            st.warning("Product code already exists!")
        return True
    return False


def remove_custom_product(product_code: str):
    """Remove custom product from the list."""
    if product_code in st.session_state["custom_products"]:
        st.session_state["custom_products"].remove(product_code)
        st.success(f"Removed product code: {product_code}")

