"""
Configuration settings for the RAG Chatbot application.
"""
import os

# API Configuration
# IMPORTANT: Set these as environment variables or in a .env file
# Never commit API keys to GitHub!
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE", "https://api.groq.com/openai/v1")

if not OPENAI_API_KEY:
    raise ValueError(
        "OPENAI_API_KEY not found! Please set it as an environment variable or in a .env file. "
        "See SETUP_INSTRUCTIONS.md for details."
    )

# Model Configuration
LLM_MODEL = "llama-3.1-8b-instant"
LLM_TEMPERATURE = 0.6

# Embedding Configuration
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_DEVICE = "cpu"

# FAISS Index Configuration
CHUNK_SIZE = 512
CHUNK_OVERLAP = 256
BATCH_SIZE = 4
MAX_WORKERS = None

# Retrieval Configuration
RETRIEVER_K_CSV = 10
RETRIEVER_K_PDF = 10
RETRIEVER_K_COMBINED = 15

# Data Paths
DATA_DIR = "data"
HIKVISION_CSV = os.path.join(DATA_DIR, "my_hikvision_data.csv")
SATEL_CSV = os.path.join(DATA_DIR, "my_satel_data.csv")

