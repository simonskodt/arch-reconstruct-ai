"""
This module provides tools for drawing UML diagrams.
"""
import os
from typing import Optional, get_args

from langchain.tools import tool
import requests
from src.agent.tools.drawing.config import (
    PLANT_UML_SERVER_URL,
    ENCODING,
    DEFAULT_OUTPUT_FORMAT,
    VALIDATION_OUTPUT_FORMAT,
    SUCCESS_STATUS_CODE,
    ExportFormats
)
from src.agent.tools.drawing.util import encode


@tool("create_uml")
def create_uml_diagram(name: str, diagram_content: str, path: str) -> str:
    """Draws a UML diagram and saves it to the specified path.

    Args:
        name: The name/title of the UML diagram
        diagram_content: The PlantUML diagram content/description
        path: The file path where to save the diagram as puml file

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
    if not file_path.endswith(".puml"):
        file_path = file_path.rsplit(".", 1)[0] + ".puml"
    if not overwrite and os.path.exists(file_path):
        return f"Error: File {file_path} already exists."
    try:
        with open(file_path, "w", encoding=ENCODING) as file:
            file.write(uml_description)
    except Exception as e:
        return f"Error saving UML file: {e}"

    return file_path

@tool
def load_uml(file_path: str) -> str:
    """Loads a UML diagram from a file.

    Args:
        file_path: Path to the UML file to load the file type has to be of type .puml

    Returns:
        The content of the UML diagram
    """
    return _load_uml(file_path)

def _load_uml(file_path: str) -> str:
    """Loads a UML diagram from a file."""
    try:
        with open(file_path, "r", encoding=ENCODING) as file:
            return file.read()
    except Exception as e:
        return f"Error loading UML file: {e}"

def _validate_uml(
        uml_diagram: str,
        format_type: ExportFormats = VALIDATION_OUTPUT_FORMAT
    ) -> str | None:
    """Validates the UML diagram syntax using the specified format.

    Returns:
        Error message if validation fails, None if valid
    """
    if not (uml_diagram.startswith("@startuml") and uml_diagram.endswith("@enduml")):
        return "Error: UML diagram must start with '@startuml' and end with '@enduml'."

    response = _export_uml(uml_diagram, None, format_type)
    if response == SUCCESS_STATUS_CODE:
        return None
    return response

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
def export_uml(
    file_path: str, output_path: str,
    format_type: ExportFormats = DEFAULT_OUTPUT_FORMAT
) -> str:
    """Exports the UML diagram to the specified format using PlantUML server."""
    return _export_uml(_load_uml(file_path), output_path, format_type)

def _export_uml(
    uml_diagram: str,
    output_path: Optional[str] = None,
    format_type: ExportFormats = DEFAULT_OUTPUT_FORMAT,
    server_url: str = PLANT_UML_SERVER_URL
) -> str :
    """Exports the UML diagram to the specified format using PlantUML server."""
    uml_content_encoded = encode(uml_diagram)
    url = f"{server_url}/{format_type}/{uml_content_encoded}"
    try:
        response = requests.get(url, timeout=20)
        # Check if the response is valid
        if response.status_code == 200:
            if output_path is None:
                return SUCCESS_STATUS_CODE
            with open(output_path, 'wb') as f:
                f.write(response.content)
            return output_path

        # an error occurred
        if format_type == VALIDATION_OUTPUT_FORMAT:
            error_msg = response.text
            return error_msg
        return f"Error {response.status_code}: \
        occured when trying to export the UML diagram as {format_type}, \
        try a another format {get_args(ExportFormats)}"

    except Exception as e:
        error_msg = f"Requests failed with error: {e}"
        return error_msg
