"""
Embedding factories (OpenAI; optional Ollama).
"""
from langchain_openai import OpenAIEmbeddings
from .config import OLLAMA_EMBEDDINGS

try:
    from langchain_ollama import OllamaEmbeddings
    OLLAMA_AVAILABLE = True
except (ImportError, ModuleNotFoundError):
    OllamaEmbeddings = None
    OLLAMA_AVAILABLE = False

def get_openai_embeddings(**kwargs):
    """Return an OpenAIEmbeddings instance."""
    return OpenAIEmbeddings(**kwargs)


def get_ollama_embeddings(model: str = OLLAMA_EMBEDDINGS[0], **kwargs):
    """Return an OllamaEmbeddings instance if available.
    Tries OLLAMA_EMBEDDINGS models in order: specified model first, then fallback list.
    """
    if not OLLAMA_AVAILABLE:
        raise RuntimeError(
            "Ollama embeddings support requires the 'langchain_ollama' package. "
            "Install it and ensure Ollama is configured."
        )
    assert OllamaEmbeddings is not None
    models_to_try = ([model] if model else []) + [m for m in OLLAMA_EMBEDDINGS if m != model]
    # Try each model until one works
    for model_name in models_to_try:
        try:
            embeddings = OllamaEmbeddings(model=model_name, **kwargs)
            embeddings.embed_query("test")  # Test model availability
            return embeddings
        except Exception as e:
            last_error = e
    # All models failed
    raise RuntimeError(
        f"Failed to initialize Ollama embeddings. Tried: {', '.join(models_to_try)}. "
        f"Last error: {last_error}. "
        f"Pull models with: ollama pull {' && ollama pull '.join(models_to_try)}"
    )

def get_default_embeddings(**kwargs):
    """Return the default embeddings provider (Ollama if available, else OpenAI)."""
    if OLLAMA_AVAILABLE:
        return get_ollama_embeddings(**kwargs)
    return get_openai_embeddings(**kwargs)
