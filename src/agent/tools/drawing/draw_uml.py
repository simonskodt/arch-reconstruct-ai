"""
This module provides tools for drawing UML diagrams.
"""
import subprocess

from langchain.tools import tool
from src.agent.tools.drawing.config import PLANT_UML_SERVER_URL, ENCODING, PREPROCESSOR_OPTION
from src.agent.tools.drawing.util import encode


@tool
def create_uml_diagram(name: str, diagram_content: str, path: str) -> str:
    """Draws a UML diagram and saves it to the specified path.

    Args:
        name: The name/title of the UML diagram
        diagram_content: The PlantUML diagram content/description
        path: The file path where to save the diagram

    Returns:
        The path where the diagram was saved
    """
    if diagram_content.startswith("@startuml") and diagram_content.endswith("@enduml"):
        if _validate_uml(diagram_content):
            return _save_uml(diagram_content, path)
    else:
        with open(path, "w", encoding=ENCODING) as file:
            file.write(f"@startuml {name}\n")
            file.write(f"{diagram_content}\n")
            file.write("@enduml\n")
            if not _validate_uml(file.read()):
                raise ValueError("Invalid UML content.")
    return path

@tool
def update_uml(uml_content: str, file_path: str) -> str:
    """Update an existing UML diagram with changes and save to file.

    Args:
        uml_content: The new UML diagram content
        file_path: Path to the existing UML file

    Returns:
        The path where the updated diagram was saved
    """
    # Load current content for validation
    current_uml = _load_uml(file_path)
    uml_status = _validate_uml(uml_content)
    if uml_status:
        return _save_uml(uml_content, file_path)

    # Revert to previous version if invalid
    _save_uml(current_uml, file_path)
    return f"Error: {uml_status}. Reverted to previous diagram at {file_path}"

@tool
def save_uml(uml_description: str, file_path: str) -> str:
    """Saves a UML diagram to a file.

    Args:
        uml_description: The complete UML diagram content
        file_path: Path where to save the diagram

    Returns:
        The path where the diagram was saved
    """
    return _save_uml(uml_description, file_path)

def _save_uml(uml_description: str, file_path: str) -> str:
    """Saves a UML diagram to a file."""
    with open(file_path, "w", encoding=ENCODING) as file:
        file.write(uml_description)

    return file_path

@tool
def load_uml(file_path: str) -> str:
    """Loads a UML diagram from a file.

    Args:
        file_path: Path to the UML file to load

    Returns:
        The content of the UML diagram
    """
    return _load_uml(file_path)

def _load_uml(file_path: str) -> str:
    """Loads a UML diagram from a file."""
    with open(file_path, "r", encoding=ENCODING) as file:
        return file.read()

def _validate_uml(uml_diagram: str) -> bool:
    """Validates the UML diagram syntax."""
    if uml_diagram.startswith("@startuml") and uml_diagram.endswith("@enduml"):
        preprocessed_diagram = _export_uml(uml_diagram, PREPROCESSOR_OPTION, "./temp.txt")
        print(preprocessed_diagram)
        return True

    raise ValueError("Missing start and end tags. @startuml ... @enduml")


@tool
def export_uml(file_path: str, format_type: str, output_path: str) -> str:
    """Exports the UML diagram to the specified format using PlantUML server.

    Args:
        file_path: Path to the UML diagram file
        format_type: Export format (png, svg, pdf, etc.)
        output_path: Path where to save the exported diagram

    Returns:
        The path where the exported diagram was saved
    """
    return _export_uml(_load_uml(file_path), format_type, output_path)

def _export_uml(uml_diagram: str,
                format_type: str,
                output_path: str,
                server_url: str = PLANT_UML_SERVER_URL
            ) -> str:
    """Exports the UML diagram to the specified format using PlantUML server."""
    uml_content_encoded = encode(uml_diagram)
    url = server_url + "/" + format_type
    subprocess.run(['curl', '-X', 'POST', '--data-binary',
                    '@-', url, '--output', output_path],
                   input=uml_content_encoded,
                   text=True,
                    check=True)
    return output_path
