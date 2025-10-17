"""
This module provides configuration settings for the drawing tools.
"""

PLANT_UML_SERVER_URL = "http://localhost:1234/plantuml"
PLANT_UML_SERVER_ENCODING = "utf-8"

ENCODING = "utf-8"

PREPROCESSOR_OPTION = "preproc" # -preproc Output preprocessor text of diagrams
EXPORT_FORMATS = ["png", "svg", "txt" ]
# "pdf", "eps", "html", "latex", "latex-nopreamble", "scxml", "utxt", "vdx", "xmi"]

# Supported export options from PlantUML:
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
