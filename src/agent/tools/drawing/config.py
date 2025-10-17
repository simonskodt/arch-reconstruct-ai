"""
This module provides configuration settings for the drawing tools.
"""
from typing import Literal

# Local file settings
ENCODING = "utf-8"

# PlantUML server configuration
PLANT_UML_SERVER_URL = "http://localhost:8080"
PLANT_UML_SERVER_ENCODING = "utf-8"
PREPROCESSOR_OPTION = 'png'
ExportFormats = Literal['png', 'svg', 'txt', 'pdf']

# Supported export options from PlantUML Local:
# --eps ........................ Generate images in EPS format
# --html ....................... Generate HTML files for class diagrams
# --latex ...................... Generate LaTeX/TikZ output
# --latex-nopreamble ........... Generate LaTeX/TikZ output without preamble
# --pdf ........................ Generate PDF images
# --png ........................ Generate PNG images (default)
# --scxml ...................... Generate SCXML files for state diagrams
# --svg ........................ Generate SVG images
# --txt ........................ Generate ASCII art diagrams
# --utxt ....................... Generate ASCII art diagrams using Unicode characters
# --vdx ........................ Generate VDX files
# --xmi ........................ Generate XMI files for class diagrams
# -preproc ..................... Output preprocessor text of diagrams
