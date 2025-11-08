# RAG Chatbot for Hikvision and Satel Products

##  Overview

This project is a **Retrieval-Augmented Generation (RAG) chatbot** that provides intelligent, context-aware answers about Hikvision and Satel security products. Built with modern AI technologies, it combines semantic search, vector databases, and large language models to deliver accurate product information and technician data.

###  What It Does

- ** Product Intelligence**: Ask natural language questions about Hikvision and Satel products and get detailed, accurate answers
- ** Product Comparison**: Search and compare product characteristics, specifications, and features
- ** Technician Agent**: Query technician information, planning schedules, and daily reports via integrated Google Drive agent
- **Intelligent Agent System**: Advanced LangChain agent that intelligently routes queries to specialized tools for technician data, planning information, and daily reports
- ** Data Collection**: Automated web scraping tools to collect and update product data from manufacturer websites

****

## Features

- **Product Queries**: Ask questions about Hikvision and Satel products
- **Product Search**: Search and compare product characteristics
- **Technician Agent**: Query technician information via integrated agent
- **RAG-based**: Uses FAISS vector stores and LangChain for semantic search
- **Multi-source**: Supports both CSV and PDF data sources
- **Web Scraping**: Scripts to collect product data from Hikvision and Satel websites

## Project Structure

```
Rag_chatbot/
├── app.py                      # Main Streamlit application
├── config/                     # Configuration files
│   ├── __init__.py
│   └── settings.py            # Application settings
├── src/                        # Source code
│   ├── agents/                # Agent modules
│   │   ├── __init__.py
│   │   └── technician_agent.py
│   ├── models/                # LLM and embedding models
│   │   ├── __init__.py
│   │   ├── llm.py
│   │   └── embeddings.py
│   ├── retrievers/            # RAG retrieval functions
│   │   ├── __init__.py
│   │   ├── index_creation.py
│   │   ├── qa_chains.py
│   │   └── product_analysis.py
│   ├── ui/                    # UI components
│   │   ├── __init__.py
│   │   ├── styles.py
│   │   └── components.py
│   └── utils/                 # Utility functions
│       ├── __init__.py
│       ├── session_state.py
│       └── search.py
├── scripts/                    # Web scraping scripts
│   ├── __init__.py
│   ├── hikvision_scraper.py   # Hikvision product scraper
│   ├── satel_scraper.py       # Satel product scraper
│   └── README.md              # Scraping scripts documentation
├── data/                      # Data files (CSV files)
│   ├── my_hikvision_data.csv
│   └── my_satel_data.csv
├── requirements.txt           # Python dependencies
├── README.md                  # This file



## Features by Category

### Technicien
- Query technician information using the integrated agent
- Chat history is maintained during the session
- Requires Google Drive API credentials (see `CREDENTIALS_SETUP.md`)

### Hikvision Product
- **Ask about an item**: Search for products and ask questions about specific items
- **Search about caractéristiques**: Search products by characteristics and compare them

### Satel Product
- **Ask about an item**: Search for products and ask questions about specific items
- **Search about caractéristiques**: Search products by characteristics and compare them



## Dependencies

- **Streamlit**: Web application framework
- **LangChain**: LLM framework and chains
- **FAISS**: Vector similarity search
- **HuggingFace**: Embedding models
- **Pandas**: Data manipulation
- **PyDrive**: Google Drive API access (for technician agent)
- **Crawl4AI**: Web scraping (optional, for data collection)

## Notes

- The application uses Groq API (via OpenAI-compatible interface) by default
- FAISS indices are cached in session state for performance
- Product indices are built on first run (may take time)
- The technician agent requires Google Drive API access (see `CREDENTIALS_SETUP.md`)
- Web scraping scripts require `crawl4ai` and `beautifulsoup4` (optional dependencies)


