"""Agent setup using an in-memory vector store for document retrieval."""
import os
from typing import List

from langchain_core.vectorstores import InMemoryVectorStore
from langchain_core.tools import create_retriever_tool
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_ollama.chat_models import ChatOllama
from langchain.agents import create_agent
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Constants
OAI_MODEL_ID = "gpt-5-nano"
OLLAMA_MODEL_ID = "mistral:latest"
PDF_PATH = os.path.join(os.path.dirname(__file__), "Rabbits and Guinea Pigs.pdf")

# Models
ollama_model = ChatOllama(model=OLLAMA_MODEL_ID)
openai_model = ChatOpenAI(model=OAI_MODEL_ID)

USE_OLLAMA = False
selected_model = ollama_model if USE_OLLAMA else openai_model

# Load simple sentences
_texts: List[str] = [
    "Dogs are great companions, "
    "known for their loyalty and friendliness.",
    "Cats are independent pets that often enjoy their own space.",
]

def load_pdf_documents(file_path: str) -> list:
    """Load and split PDF documents."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"PDF file not found: {file_path}")
    loader = PyPDFLoader(file_path)
    docs = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=400, chunk_overlap=50, add_start_index=True
    )
    return text_splitter.split_documents(docs)

# Load PDF
all_splits = load_pdf_documents(PDF_PATH)

# Setup vector store
_embeddings = OpenAIEmbeddings()
vector_store: InMemoryVectorStore = InMemoryVectorStore(_embeddings)

vector_store.add_texts(_texts)
vector_store.add_documents(all_splits)

document_tool = create_retriever_tool(
    vector_store.as_retriever(),
    "pet_information_retriever",
    "Fetches information about pets (dogs, cats, rabbits, and guinea pigs)."
)

# Create agent
agent = create_agent(
    selected_model,
    tools=[document_tool],
    system_prompt=f"""Act as an assistant.
        Call the {document_tool.name} (description: {document_tool.description})
        that you have available to answer questions on animals.""",
)
