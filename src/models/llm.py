"""
LLM model initialization and configuration.
"""
from langchain.chat_models import ChatOpenAI
from config.settings import OPENAI_API_KEY, OPENAI_API_BASE, LLM_MODEL, LLM_TEMPERATURE
import os

# Set environment variables
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
os.environ["OPENAI_API_BASE"] = OPENAI_API_BASE


def get_llm():
    """Initialize and return the LLM model."""
    return ChatOpenAI(
        model=LLM_MODEL,
        temperature=LLM_TEMPERATURE,
    )

