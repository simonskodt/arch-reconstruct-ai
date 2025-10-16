"""
Create an VectorStore and wrap its retriever as a LangChain tool.
"""
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_core.tools import create_retriever_tool
from langchain_community.vectorstores import Chroma

from .embeddings import get_default_embeddings
from .loaders import load_pdf_documents
from .config import DEFAULT_CHROMA_DB, DEFAULT_COLLECTION_NAME

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

def create_inmemory_vector_store(embeddings=None,
                                 texts: list[str] | None = None,
                                 documents: list | None = None):
    """
    Create and optionally populate an in-memory vector store.

    Args:
        embeddings: An embeddings provider instance. If None, a default OpenAI
            embeddings instance is created via get_ollama_embeddings().
        texts: Optional list of raw text strings to add to the store.
        documents: Optional list of LangChain Document objects to add to the store.

    Returns:
        An initialized InMemoryVectorStore with any provided texts/documents ingested.
    """
    embeddings = embeddings or get_default_embeddings()
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

# pylint: disable=too-many-arguments,too-many-positional-arguments
def create_persistent_vector_store_from_pdf(embeddings,
                                            pdf_path: str,
                                            save_path: str = DEFAULT_CHROMA_DB,
                                            collection_name: str = DEFAULT_COLLECTION_NAME,
                                            chunk_size: int = 400,
                                            chunk_overlap: int = 50):
    """
    Load a PDF, split it into chunks, create a ChromaDB vector store, and save it locally.

    Args:
        pdf_path: Filesystem path to the PDF to ingest.
        save_path: Directory path to save the ChromaDB vector store.
        collection_name: Name for the ChromaDB collection.
        embeddings: Embeddings provider instance (required to ensure consistency).
        chunk_size: Token/character chunk size for the splitter.
        chunk_overlap: Overlap size between chunks.

    Returns:
        A ChromaDB vector store populated with vectorized PDF chunks, saved locally.
    """
    docs = load_pdf_documents(pdf_path, chunk_size, chunk_overlap)

    # Create ChromaDB store
    store = Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory=save_path
    )

    # Add documents
    store.add_documents(docs)

    return store

def load_persistent_vector_store(embeddings,
                                 save_path: str = DEFAULT_CHROMA_DB,
                                 collection_name: str = DEFAULT_COLLECTION_NAME):
    """
    Load a previously saved ChromaDB vector store from local disk.

    Args:
        save_path: Directory path where the ChromaDB vector store was saved.
        collection_name: Name of the ChromaDB collection to load.
        embeddings: Embeddings provider instance (must be the same as used for creation).

    Returns:
        A ChromaDB vector store loaded with vectorized documents.
    """

    try:
        store = Chroma(
            collection_name=collection_name,
            embedding_function=embeddings,
            persist_directory=save_path
        )
        return store
    except Exception as e:
        raise RuntimeError(f"Failed to load ChromaDB store from {save_path}: {e}") from e
