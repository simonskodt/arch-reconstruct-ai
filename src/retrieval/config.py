"""
Configuration constants for the retrieval subsystem:
default chunking, embedding provider, and model settings.
"""

# Defaults
DEFAULT_CHUNK_SIZE = 400
DEFAULT_CHUNK_OVERLAP = 50
DEFAULT_EMBEDDING = "openai"
DEFAULT_MODEL = "gpt-5-nano"
PDF_SPLIT_SETTINGS = {"chunk_size": DEFAULT_CHUNK_SIZE, "chunk_overlap": DEFAULT_CHUNK_OVERLAP}

# Alternatives
OPENAI_MODEL_ALT = "gpt-4.1-nano"
ANTHROPIC_MODEL = "claude-3-mini"
OLLAMA_MODEL = "mistral:latest"
OLLAMA_EMBEDDING = "nomic-embed-text:v1.5"
