"""
Create an InMemoryVectorStore and wrap its retriever as a LangChain tool.
"""

from typing import List, Optional
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_core.tools import create_retriever_tool
from .embeddings import get_openai_embeddings
from .loaders import load_pdf_documents

def create_inmemory_vector_store(embeddings=None,
                                 texts: Optional[List[str]] = None,
                                 documents: Optional[List] = None):
    """
    Create and optionally populate an in-memory vector store.

    Args:
        embeddings: An embeddings provider instance. If None, a default OpenAI
            embeddings instance is created via get_openai_embeddings().
        texts: Optional list of raw text strings to add to the store.
        documents: Optional list of LangChain Document objects to add to the store.

    Returns:
        An initialized InMemoryVectorStore with any provided texts/documents ingested.
    """
    embeddings = embeddings or get_openai_embeddings()
    store = InMemoryVectorStore(embeddings)

    if texts:
        store.add_texts(texts)
    if documents:
        store.add_documents(documents=documents)

    return store

def create_vector_store_from_pdf(pdf_path: str,
                                 embeddings=None,
                                 chunk_size: int = 400,
                                 chunk_overlap: int = 50):
    """
    Load a PDF, split it into chunks, and create an in-memory vector store.

    Args:
        pdf_path: Filesystem path to the PDF to ingest.
        embeddings: Optional embeddings provider; falls back to default if None.
        chunk_size: Token/character chunk size for the splitter.
        chunk_overlap: Overlap size between chunks.

    Returns:
        An InMemoryVectorStore populated with vectorized PDF chunks.
    """
    docs = load_pdf_documents(pdf_path, chunk_size=chunk_size, chunk_overlap=chunk_overlap)

    return create_inmemory_vector_store(embeddings=embeddings, documents=docs)

def create_retriever_tool_from_store(store,
                                     name: str,
                                     description: str):
    """
    Wrap a vector store's retriever as a LangChain tool.

    Args:
        store: A vector store instance exposing .as_retriever().
        name: Tool name to register (used by agents/tools lists).
        description: Short description of the tool's purpose.

    Returns:
        A LangChain Tool that calls the store retriever.
    """
    return create_retriever_tool(store.as_retriever(), name, description)
