"""
src.retrieval — Retrieval utilities: embeddings, loaders, vector stores, memory and RAG helpers.
"""

__version__ = "0.1.0"

from .config import *
from .embeddings import get_openai_embeddings, get_ollama_embeddings
from .loaders import load_pdf_documents
from .vector_store import (
    create_inmemory_vector_store,
    create_vector_store_from_pdf,
    create_retriever_tool_from_store
)

__all__ = [
    "get_openai_embeddings",
    "get_ollama_embeddings",
    "load_pdf_documents",
    "create_inmemory_vector_store",
    "create_vector_store_from_pdf",
    "create_retriever_tool_from_store",
]
