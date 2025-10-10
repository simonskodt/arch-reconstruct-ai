"""
Embedding factories (OpenAI; optional Ollama).
"""

from langchain_openai import OpenAIEmbeddings

try:
    from langchain_ollama import OllamaEmbeddings
    OLLAMA_AVAILABLE = True
except (ImportError, ModuleNotFoundError):
    OllamaEmbeddings = None
    OLLAMA_AVAILABLE = False

def get_openai_embeddings(**kwargs):
    """Return an OpenAIEmbeddings instance."""
    return OpenAIEmbeddings(**kwargs)

def get_ollama_embeddings(**kwargs):
    """Return an OllamaEmbeddings instance if available, else raise."""
    if not OLLAMA_AVAILABLE:
        raise RuntimeError(
            "Ollama embeddings support requires the 'langchain_ollama' package. "
            "Install it and ensure Ollama is configured."
        )
    return OllamaEmbeddings(**kwargs)
