"""
Main Streamlit application for RAG Chatbot.
Supports Hikvision and Satel products, plus technician queries via agent.
"""
import streamlit as st
import pandas as pd
from src.models.llm import get_llm
from src.models.embeddings import get_embedding_model
from src.retrievers.index_creation import (
    create_product_index,
    create_enhanced_specs_index_accelerated,
    create_enhanced_specs_index_accelerated_pdf,
    create_enhanced_specs_index_accelerated_satel,
    create_enhanced_specs_index_accelerated_pdf_satel
)
from src.ui.styles import STYLES
from src.ui.components import (
    render_technician_interface,
    render_product_chat,
    render_product_search_interface
)
from src.utils.session_state import initialize_session_state
from config.settings import HIKVISION_CSV, SATEL_CSV


# Apply styles
st.markdown(STYLES, unsafe_allow_html=True)

# Initialize session state
initialize_session_state()

# Load embedding model
embedding_model = get_embedding_model()

# Load data
try:
    df_hikvision = pd.read_csv(HIKVISION_CSV)
    # Limit to first 20 rows for testing (remove in production)
    if len(df_hikvision) > 20:
        df_hikvision = df_hikvision[:20]
except FileNotFoundError:
    st.error(f"❌ File not found: {HIKVISION_CSV}")
    st.stop()

try:
    df_satel = pd.read_csv(SATEL_CSV)
except FileNotFoundError:
    st.error(f"❌ File not found: {SATEL_CSV}")
    st.stop()

# Create product indices
if 'product_index_hikvision' not in st.session_state:
    st.session_state['product_index_hikvision'] = create_product_index(df_hikvision, embedding_model)

if 'product_index_satel' not in st.session_state:
    st.session_state['product_index_satel'] = create_product_index(df_satel, embedding_model)

product_index_hikvision = st.session_state['product_index_hikvision']
product_index_satel = st.session_state['product_index_satel']

# Create specs indices
with st.spinner("⚡ Building/loading product indexes, please wait..."):
    if 'specs_index_hikvision' not in st.session_state:
        st.session_state['specs_index_hikvision'] = create_enhanced_specs_index_accelerated(
            df_hikvision, embedding_model, batch_size=4, max_workers=None
        )
        st.success("✅ specs_index_hikvision loaded successfully")
    
    if 'specs_index_pdf_hikvision' not in st.session_state:
        st.session_state['specs_index_pdf_hikvision'] = create_enhanced_specs_index_accelerated_pdf(
            df_hikvision, embedding_model, batch_size=4, max_workers=None
        )
        st.success("✅ specs_index_pdf_hikvision loaded successfully")
    
    if 'specs_index_satel' not in st.session_state:
        st.session_state['specs_index_satel'] = create_enhanced_specs_index_accelerated_satel(
            df_satel, embedding_model, batch_size=4, max_workers=None
        )
        st.success("✅ specs_index_satel loaded successfully")
    
    if 'specs_index_pdf_satel' not in st.session_state:
        st.session_state['specs_index_pdf_satel'] = create_enhanced_specs_index_accelerated_pdf_satel(
            df_satel, embedding_model, batch_size=4, max_workers=None
        )
        st.success("✅ specs_index_pdf_satel loaded successfully")

specs_index_hikvision = st.session_state['specs_index_hikvision']
specs_index_pdf_hikvision = st.session_state['specs_index_pdf_hikvision']
specs_index_satel = st.session_state['specs_index_satel']
specs_index_pdf_satel = st.session_state['specs_index_pdf_satel']

# Initialize LLM
llm = get_llm()

# Sidebar Menu
st.sidebar.title("Select Category")
category = st.sidebar.radio(
    "Choose a category:",
    ("Technicien", "Satel Product", "Hikvision Product")
)

# Main Interface
st.markdown('<div class="main-title">Interactive Chatbot</div>', unsafe_allow_html=True)

# Route to appropriate interface
if category == "Technicien":
    render_technician_interface()

elif category == "Hikvision Product":
    st.markdown(f'<div class="section-title">{category} Queries</div>', unsafe_allow_html=True)
    
    action = st.radio(
        "Choose an action:",
        ("Ask about an item", "Search about caractéristiques")
    )
    
    if action == "Ask about an item":
        product_query = st.text_input(f"Enter the product code or query about {category} items:")
        
        if product_query:
            # Search in FAISS index
            results = product_index_hikvision.similarity_search(product_query, k=3)
            
            if results:
                # Extract product_code and product_name from metadata
                extracted = [
                    {
                        "product_code": r.metadata.get("product_code", ""),
                        "product_name": r.metadata.get("product_name", "")
                    }
                    for r in results
                ]
                df_results = pd.DataFrame(extracted)
                
                st.markdown("### Top results for your query:")
                st.dataframe(df_results, use_container_width=True)
                
                # Let the user select a product
                selected_code = st.radio("Select a product to ask questions about:", df_results['product_code'])
                
                if selected_code:
                    render_product_chat(
                        selected_code,
                        category,
                        llm,
                        specs_index_hikvision,
                        specs_index_pdf_hikvision,
                        embedding_model
                    )
            else:
                st.markdown(
                    f'<div class="chat-response">No results found for "{product_query}".</div>',
                    unsafe_allow_html=True
                )
    
    elif action == "Search about caractéristiques":
        render_product_search_interface(
            category,
            df_hikvision,
            llm,
            specs_index_hikvision,
            specs_index_pdf_hikvision,
            embedding_model
        )

elif category == "Satel Product":
    st.markdown(f'<div class="section-title">{category} Queries</div>', unsafe_allow_html=True)
    
    action = st.radio(
        "Choose an action:",
        ("Ask about an item", "Search about caractéristiques")
    )
    
    if action == "Ask about an item":
        product_query = st.text_input(f"Enter the product code or query about {category} items:")
        
        if product_query:
            # Search in FAISS index
            results = product_index_satel.similarity_search(product_query, k=3)
            
            if results:
                # Extract product_code and product_name from metadata
                extracted = [
                    {
                        "product_code": r.metadata.get("product_code", ""),
                        "product_name": r.metadata.get("product_name", "")
                    }
                    for r in results
                ]
                df_results = pd.DataFrame(extracted)
                
                st.markdown("### Top results for your query:")
                st.dataframe(df_results, use_container_width=True)
                
                # Let the user select a product
                selected_code = st.radio("Select a product to ask questions about:", df_results['product_code'])
                
                if selected_code:
                    render_product_chat(
                        selected_code,
                        category,
                        llm,
                        specs_index_satel,
                        specs_index_pdf_satel,
                        embedding_model
                    )
            else:
                st.markdown(
                    f'<div class="chat-response">No results found for "{product_query}".</div>',
                    unsafe_allow_html=True
                )
    
    elif action == "Search about caractéristiques":
        render_product_search_interface(
            category,
            df_satel,
            llm,
            specs_index_satel,
            specs_index_pdf_satel,
            embedding_model
        )

