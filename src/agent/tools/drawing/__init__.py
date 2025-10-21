"""This module provides tools for drawing uml diagrams."""

from .draw_uml import (
    create_uml_diagram,
    load_uml,
    export_uml,
)

def get_drawing_tools():
    """Returns a list of drawing tools."""
    return [
        create_uml_diagram,
        load_uml,
        export_uml,
]

__all__ = [
    "create_uml_diagram",
    "load_uml",
    "export_uml",
]
