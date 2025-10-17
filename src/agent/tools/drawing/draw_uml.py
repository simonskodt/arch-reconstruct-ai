"""
This module provides tools for drawing UML diagrams.
"""
import os
from typing import Optional

from langchain.tools import tool
import requests
from src.agent.tools.drawing.config import (
    PLANT_UML_SERVER_URL,
    ENCODING,
    PREPROCESSOR_OPTION,
    ExportFormats
)
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
    # Ensure the diagram content has proper UML tags
    full_content = _ensure_uml_tags(diagram_content, name)
    if (err_msg := _validate_uml(full_content)):
        return err_msg
    return _save_uml(full_content, path, False)



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
    if (err_msg := _validate_uml(uml_content)):
        return err_msg
    return _save_uml(uml_content, file_path, True)

@tool
def save_uml(uml_description: str, file_path: str, overwrite: bool = False) -> str:
    """Saves a UML diagram to a file.

    Args:
        uml_description: The complete UML diagram content
        file_path: Path where to save the diagram
        overwrite: Whether to overwrite the file if it exists

    Returns:
        The path where the diagram was saved
    """
    return _save_uml(uml_description, file_path, overwrite)

def _save_uml(uml_description: str, file_path: str, overwrite: bool) -> str:
    """Saves a UML diagram to a file."""
    if not overwrite and os.path.exists(file_path):
        return f"Error: File {file_path} already exists."

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

def _validate_uml(uml_diagram: str) -> str | None:
    """Validates the UML diagram syntax."""
    if uml_diagram.startswith("@startuml") and uml_diagram.endswith("@enduml"):
        result = _export_uml(uml_diagram, PREPROCESSOR_OPTION, None)
        if isinstance(result, str) and "Syntax Error" in result:
            return result
        return None
    return "Error: UML diagram must start with '@startuml' and end with '@enduml'."

def _ensure_uml_tags(diagram_content: str, name: str) -> str:
    """Ensures the UML diagram content has proper start and end tags."""
    if not diagram_content.startswith("@startuml"):
        diagram_content = f"@startuml {name}\n{diagram_content}"
    if not diagram_content.endswith("@enduml"):
        diagram_content = f"{diagram_content}\n@enduml"
    return diagram_content

@tool(description=""" \
    Exports the UML diagram to the specified format using PlantUML server.

    Args:
        file_path: Path to the UML diagram file
        format_type: Export format ({ExportFormats})
        output_path: Optional path where to save the exported diagram. If None, returns the raw content.

    Returns:
        The path where the exported diagram was saved, or the raw content/error message if output_path is None
    """)
def export_uml(file_path: str, format_type: ExportFormats, output_path: str | None) -> str:
    """Exports the UML diagram to the specified format using PlantUML server."""
    return _export_uml(_load_uml(file_path), format_type, output_path)

def _export_uml(
    uml_diagram: str,
    format_type: ExportFormats,
    output_path: Optional[str],
    server_url: str = PLANT_UML_SERVER_URL
) -> str :
    """Exports the UML diagram to the specified format using PlantUML server."""
    uml_content_encoded = encode(uml_diagram)
    url = f"{server_url}/{format_type}/{uml_content_encoded}"
    try:
        response = requests.get(url, timeout=20)
        if response.status_code == 200:
            if output_path is None:
                return response.content.decode(ENCODING)
            with open(output_path, 'wb') as f:
                f.write(response.content)
            return output_path
        error_msg = response.text
        return error_msg
    except Exception as e:
        error_msg = f"Requests failed with error: {e}"
        return error_msg
