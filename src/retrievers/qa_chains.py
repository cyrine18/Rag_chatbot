"""
Question-answering chains for product queries.
"""
from langchain.chains import RetrievalQA
from langchain.vectorstores import FAISS
from config.settings import RETRIEVER_K_CSV, RETRIEVER_K_PDF, RETRIEVER_K_COMBINED


def ask_product_question(product_code: str, query: str, llm, specs_index: dict, specs_index_pdf: dict, embedding_model):
    """
    Ask a question about a Hikvision product.
    
    Args:
        product_code: Product code to query
        query: User question
        llm: Language model instance
        specs_index: Dictionary of CSV-based FAISS indices
        specs_index_pdf: Dictionary of PDF-based FAISS indices
        embedding_model: Embedding model instance
    
    Returns:
        Dictionary with 'result' and 'source_documents'
    """
    final_docs = []
    
    # Step 1: Search in CSV/text embeddings
    if product_code in specs_index:
        retriever_csv = specs_index[product_code].as_retriever(search_kwargs={"k": RETRIEVER_K_CSV})
        docs_csv = retriever_csv.get_relevant_documents(query)
        final_docs.extend(docs_csv)
    
    # Step 2: Search in PDF embeddings
    if product_code in specs_index_pdf:
        retriever_pdf = specs_index_pdf[product_code].as_retriever(search_kwargs={"k": RETRIEVER_K_PDF})
        docs_pdf = retriever_pdf.get_relevant_documents(query)
        final_docs.extend(docs_pdf)
    
    # Step 3: Create a temporary retriever from combined docs
    combined_index = FAISS.from_documents(final_docs, embedding_model)
    combined_retriever = combined_index.as_retriever(search_kwargs={"k": RETRIEVER_K_COMBINED})
    
    # Step 4: Feed to LLM
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=combined_retriever,
        return_source_documents=True
    )
    
    result = qa_chain(query)
    return result


def ask_product_question_satel(product_code: str, query: str, llm, specs_index_satel: dict, specs_index_pdf_satel: dict, embedding_model):
    """
    Ask a question about a Satel product.
    
    Args:
        product_code: Product code to query
        query: User question
        llm: Language model instance
        specs_index_satel: Dictionary of CSV-based FAISS indices for Satel
        specs_index_pdf_satel: Dictionary of PDF-based FAISS indices for Satel
        embedding_model: Embedding model instance
    
    Returns:
        Dictionary with 'result' and 'source_documents'
    """
    final_docs = []
    
    # Step 1: Search in CSV/text embeddings
    if product_code in specs_index_satel:
        retriever_csv = specs_index_satel[product_code].as_retriever(search_kwargs={"k": RETRIEVER_K_CSV})
        docs_csv = retriever_csv.get_relevant_documents(query)
        final_docs.extend(docs_csv)
    
    # Step 2: Search in PDF embeddings
    if product_code in specs_index_pdf_satel:
        retriever_pdf = specs_index_pdf_satel[product_code].as_retriever(search_kwargs={"k": RETRIEVER_K_PDF})
        docs_pdf = retriever_pdf.get_relevant_documents(query)
        final_docs.extend(docs_pdf)
    
    # Step 3: Create a temporary retriever from combined docs
    combined_index = FAISS.from_documents(final_docs, embedding_model)
    combined_retriever = combined_index.as_retriever(search_kwargs={"k": RETRIEVER_K_COMBINED})
    
    # Step 4: Feed to LLM
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=combined_retriever,
        return_source_documents=True
    )
    
    result = qa_chain(query)
    return result

