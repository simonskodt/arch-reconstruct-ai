"""
Load a PDF and split its content into chunked documents for vector ingestion.
"""

import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from .config import DEFAULT_CHUNK_SIZE, DEFAULT_CHUNK_OVERLAP

def load_pdf_documents(file_path: str,
                       chunk_size: int = DEFAULT_CHUNK_SIZE,
                       chunk_overlap: int = DEFAULT_CHUNK_OVERLAP):
    """Load and split a PDF into documents ready for vector ingestion."""

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"PDF file not found: {file_path}")

    loader = PyPDFLoader(file_path)
    docs = loader.load()
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        add_start_index=True)

    return splitter.split_documents(docs)
