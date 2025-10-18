"""
Build in-memory vector stores and retriever tools for standard knowledge bases.
"""
from pathlib import Path
from src.retrieval.embeddings import get_ollama_embeddings
from src.retrieval.loaders import load_pdf_documents
from src.retrieval.vector_store import (
    create_inmemory_vector_store,
    create_retriever_tool_from_store,
    create_persistent_vector_store_from_pdf,
    load_persistent_vector_store
)
from src.retrieval.config import DEFAULT_CHROMA_DB

_BASE_DIR = Path(__file__).parent
emb = get_ollama_embeddings()


# Architecture KB
arch_pdf = (
    _BASE_DIR
    / "architecture_kb"
    / "An Approach to Software Architecture Description Using UML.pdf"
)
if arch_pdf.exists():
    arch_docs = load_pdf_documents(
        str(arch_pdf),
        chunk_size=800,
        chunk_overlap=120,
    )
    arch_store = create_inmemory_vector_store(emb, documents=arch_docs)
    arch_tool = create_retriever_tool_from_store(
        arch_store,
        name="architecture_retriever",
        description="Retrieve software architecture and reconstruction concepts."
    )


# Diagrams
DIAGRAM_STORE_PATH = f"{DEFAULT_CHROMA_DB}_{emb.model}"
DIAGRAM_COLLECTION_NAME = "diagram_store"
DIAGRAM_DOCS_PATH = \
"C:\\Users\\thoma\\Desktop\\arch-reconstruct-ai\\PlantUML_Language_Reference_Guide_en.pdf"

if Path(DIAGRAM_STORE_PATH).exists():
    diag_store = load_persistent_vector_store(emb, DIAGRAM_STORE_PATH, DIAGRAM_COLLECTION_NAME)
else:
    diag_docs = load_pdf_documents(DIAGRAM_DOCS_PATH, chunk_size=500, chunk_overlap=75)

    diag_store = create_persistent_vector_store_from_pdf(embeddings=emb,
        pdf_path=DIAGRAM_DOCS_PATH,
        save_path=DIAGRAM_STORE_PATH,
        collection_name=DIAGRAM_COLLECTION_NAME,
    )

diag_tool = create_retriever_tool_from_store(
    diag_store,
    name="diagram_retriever",
    description="Retrieve diagram syntax and examples (Mermaid, UML)."
)

tools = [diag_tool]
