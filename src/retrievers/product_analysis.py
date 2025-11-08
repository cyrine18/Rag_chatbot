"""
Product analysis functions for comparing products.
"""
import pandas as pd
from langchain.prompts import PromptTemplate
from config.settings import RETRIEVER_K_CSV, RETRIEVER_K_PDF


def search_selected_products_tool_dual_df(query: str, selected_codes: list, llm, specs_index: dict, specs_index_pdf: dict):
    """
    Analyze products and return a DataFrame with code, correspond and justification for Hikvision.
    
    Args:
        query: User question
        selected_codes: List of product codes to analyze
        llm: Language model instance
        specs_index: Dictionary of CSV-based FAISS indices
        specs_index_pdf: Dictionary of PDF-based FAISS indices
    
    Returns:
        DataFrame with columns: code, correspond, justification, soures
    """
    decision_prompt = PromptTemplate(
        input_variables=["context", "question", "product_code"],
        template="""
Vous êtes un ASSISTANT IA SPÉCIALISÉ en caméras de surveillance et systèmes de sécurité.
Produit à analyser : {product_code}

Spécifications techniques (CSV) :
{context}

Question : {question}

INSTRUCTIONS :
- Répondez OUI ou NON de manière FACTUELLE et PRÉCISE.
- Justifiez votre réponse même si c'est NON.
- Si vous n'êtes pas sûr ou si les informations sont insuffisantes, répondez "Pas clair".
RÉPONSE :
"""
    )

    pdf_prompt = PromptTemplate(
        input_variables=["context", "question", "product_code"],
        template="""
Vous êtes un ASSISTANT IA SPÉCIALISÉ en caméras de surveillance et systèmes de sécurité.
Produit à analyser : {product_code}

Spécifications techniques (PDF) :
{context}

Question : {question}

INSTRUCTIONS :
- Répondez de manière FACTUELLE et PRÉCISE.
- Justifiez votre réponse même si c'est NON.
- Utilisez toutes les informations disponibles dans le PDF.
RÉPONSE :
"""
    )

    results = []

    for product_code in selected_codes:
        try:
            final_docs_csv = []
            context_df = ""
            # CSV retriever
            if product_code in specs_index:
                retriever_csv = specs_index[product_code].as_retriever(search_kwargs={"k": 5})
                docs_csv = retriever_csv.get_relevant_documents(query)
                final_docs_csv.extend(docs_csv)

            # Première analyse CSV
            if not final_docs_csv:
                first_response = "Pas clair"
                context_csv = ""
            else:
                context_csv = "\n".join([doc.page_content for doc in final_docs_csv])
                context_df = context_csv
                prompt_input_csv = decision_prompt.format(
                    context=context_csv,
                    question=query,
                    product_code=product_code
                )
                first_response = llm.invoke(prompt_input_csv).content.strip()

            # PDF fallback si "Pas clair"
            if "pas clair" in first_response.lower():
                final_docs_pdf = []
                if product_code in specs_index_pdf:
                    retriever_pdf = specs_index_pdf[product_code].as_retriever(search_kwargs={"k": RETRIEVER_K_PDF})
                    docs_pdf = retriever_pdf.get_relevant_documents(query)
                    final_docs_pdf.extend(docs_pdf)

                if final_docs_pdf:
                    context_pdf = "\n".join([doc.page_content for doc in final_docs_pdf])
                    context_df = context_pdf
                    prompt_input_pdf = pdf_prompt.format(
                        context=context_pdf,
                        question=query,
                        product_code=product_code
                    )
                    llm_response = llm.invoke(prompt_input_pdf).content.strip()
                else:
                    llm_response = first_response
            else:
                llm_response = first_response

            # Déterminer correspondance (oui/non)
            if "oui" in llm_response.lower():
                correspond = "Oui"
            else:
                correspond = "Non"

            results.append({
                "code": product_code,
                "correspond": correspond,
                "justification": llm_response,
                "soures": context_df
            })

        except Exception as e:
            results.append({
                "code": product_code,
                "correspond": "Erreur",
                "justification": str(e)
            })
            continue

    return pd.DataFrame(results)


def search_selected_products_tool_dual_df_satel(query: str, selected_codes: list, llm, specs_index_satel: dict, specs_index_pdf_satel: dict):
    """
    Analyze products and return a DataFrame with code, correspond and justification for Satel.
    
    Args:
        query: User question
        selected_codes: List of product codes to analyze
        llm: Language model instance
        specs_index_satel: Dictionary of CSV-based FAISS indices for Satel
        specs_index_pdf_satel: Dictionary of PDF-based FAISS indices for Satel
    
    Returns:
        DataFrame with columns: code, correspond, justification, soures
    """
    decision_prompt = PromptTemplate(
        input_variables=["context", "question", "product_code"],
        template="""
Vous êtes un ASSISTANT IA SPÉCIALISÉ en caméras de surveillance et systèmes de sécurité.
Produit à analyser : {product_code}

Spécifications techniques (CSV) :
{context}

Question : {question}

INSTRUCTIONS :
- Répondez OUI ou NON de manière FACTUELLE et PRÉCISE.
- Justifiez votre réponse même si c'est NON.
- Si vous n'êtes pas sûr ou si les informations sont insuffisantes, répondez "Pas clair".
RÉPONSE :
"""
    )

    pdf_prompt = PromptTemplate(
        input_variables=["context", "question", "product_code"],
        template="""
Vous êtes un ASSISTANT IA SPÉCIALISÉ en caméras de surveillance et systèmes de sécurité.
Produit à analyser : {product_code}

Spécifications techniques (PDF) :
{context}

Question : {question}

INSTRUCTIONS :
- Répondez de manière FACTUELLE et PRÉCISE.
- Justifiez votre réponse même si c'est NON.
- Utilisez toutes les informations disponibles dans le PDF.
RÉPONSE :
"""
    )

    results = []

    for product_code in selected_codes:
        try:
            final_docs_csv = []
            context_df = ""
            # CSV retriever
            if product_code in specs_index_satel:
                retriever_csv = specs_index_satel[product_code].as_retriever(search_kwargs={"k": 5})
                docs_csv = retriever_csv.get_relevant_documents(query)
                final_docs_csv.extend(docs_csv)

            # Première analyse CSV
            if not final_docs_csv:
                first_response = "Pas clair"
                context_csv = ""
            else:
                context_csv = "\n".join([doc.page_content for doc in final_docs_csv])
                context_df = context_csv
                prompt_input_csv = decision_prompt.format(
                    context=context_csv,
                    question=query,
                    product_code=product_code
                )
                first_response = llm.invoke(prompt_input_csv).content.strip()

            # PDF fallback si "Pas clair"
            if "pas clair" in first_response.lower():
                final_docs_pdf = []
                if product_code in specs_index_pdf_satel:
                    retriever_pdf = specs_index_pdf_satel[product_code].as_retriever(search_kwargs={"k": RETRIEVER_K_PDF})
                    docs_pdf = retriever_pdf.get_relevant_documents(query)
                    final_docs_pdf.extend(docs_pdf)

                if final_docs_pdf:
                    context_pdf = "\n".join([doc.page_content for doc in final_docs_pdf])
                    context_df = context_pdf
                    prompt_input_pdf = pdf_prompt.format(
                        context=context_pdf,
                        question=query,
                        product_code=product_code
                    )
                    llm_response = llm.invoke(prompt_input_pdf).content.strip()
                else:
                    llm_response = first_response
            else:
                llm_response = first_response

            # Déterminer correspondance (oui/non)
            if "oui" in llm_response.lower():
                correspond = "Oui"
            else:
                correspond = "Non"

            results.append({
                "code": product_code,
                "correspond": correspond,
                "justification": llm_response,
                "soures": context_df
            })

        except Exception as e:
            results.append({
                "code": product_code,
                "correspond": "Erreur",
                "justification": str(e)
            })
            continue

    return pd.DataFrame(results)

