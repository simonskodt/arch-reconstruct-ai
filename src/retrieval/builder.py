"""
Build in-memory vector stores and retriever tools for standard knowledge bases.
"""

from pathlib import Path
from .embeddings import get_openai_embeddings
from .loaders import load_pdf_documents
from .vector_store import (
    create_inmemory_vector_store,
    create_retriever_tool_from_store,
)

_BASE_DIR = Path(__file__).parent
emb = get_openai_embeddings()

# Architecture KB
arch_pdf = (
    _BASE_DIR
    / "architecture_kb"
    / "An Approach to Software Architecture Description Using UML.pdf"
)
arch_docs = load_pdf_documents(
    str(arch_pdf),
    chunk_size=800,
    chunk_overlap=120,
)
arch_store = create_inmemory_vector_store(embeddings=emb, documents=arch_docs)
arch_tool = create_retriever_tool_from_store(
    arch_store,
    name="architecture_retriever",
    description="Retrieve software architecture and reconstruction concepts."
)

# Diagrams KB
"""
diag_docs = load_pdf_documents("path/to/mermaid_uml.pdf", chunk_size=500, chunk_overlap=75)
diag_store = create_inmemory_vector_store(embeddings=emb, documents=diag_docs)
diag_tool = create_retriever_tool_from_store(
    diag_store,
    name="diagram_retriever",
    description="Retrieve diagram syntax and examples (Mermaid, UML)."
)
"""

tools = [arch_tool]
