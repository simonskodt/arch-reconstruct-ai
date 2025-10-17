"""Utility functions for service availability checks."""
import warnings
import requests
from langchain_ollama import OllamaEmbeddings
from src.retrieval.config import OLLAMA_EMBEDDINGS
from src.agent.tools.drawing.config import PLANT_UML_SERVER_URL

def check_service_availability():
    """Check if either Ollama or PlantUML server is available and warn if neither is running."""
    # Check Ollama availability by trying to create and test an embeddings client
    ollama_available = False
    try:
        # Try to create embeddings client and test it
        embeddings = OllamaEmbeddings(model=OLLAMA_EMBEDDINGS[0])
        embeddings.embed_query("test")  # This will fail if Ollama isn't running
        ollama_available = True
    except Exception:
        ollama_available = False

    # Check PlantUML server
    plantuml_available = False
    try:
        response = requests.get(f"{PLANT_UML_SERVER_URL}/", timeout=10,)
        plantuml_available = response.status_code == 200
    except Exception:
        plantuml_available = False

    plant_uml_message = "Run \
        'docker run -d -p 8080:8080 --name plantumlserver plantuml/plantuml-server:jetty'\n" \
        "The agent will still work but with reduced functionality."

    if not ollama_available and not plantuml_available:
        warnings.warn(
            "WARNING: Neither Ollama nor PlantUML server is available!\n"
            "This may limit the agent's capabilities:\n"
            "- Ollama is needed for local embeddings and AI model inference\n"
            "- PlantUML server is needed for UML diagram generation\n\n"
            "To fix this:\n"
            "1. For Ollama: Install Ollama and run 'ollama serve'\n"
            "2. For PlantUML: {plant_uml_message}\n",

            UserWarning,
            stacklevel=2
        )
    elif not ollama_available:
        warnings.warn(
            "WARNING: Ollama is not available. Local embeddings and AI inference will not work.\n"
            "Install Ollama and run 'ollama serve' to enable these features.",
            UserWarning,
            stacklevel=2
        )
    elif not plantuml_available:
        warnings.warn(
            "WARNING: PlantUML server is not available. UML diagram generation will not work.\n"
            f"{plant_uml_message}",
            UserWarning,
            stacklevel=2
        )
