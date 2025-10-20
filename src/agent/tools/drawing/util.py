"""Utility functions for encoding PlantUML diagrams."""
import base64
import string
from zlib import compress
from src.agent.tools.drawing.config import PLANT_UML_SERVER_ENCODING

maketrans = bytes.maketrans
PLANTUML_ALPHABET = string.digits + string.ascii_uppercase + string.ascii_lowercase + '-_'
BASE64_ALPHABET   = string.ascii_uppercase + string.ascii_lowercase + string.digits + '+/'
B64_TO_PLANTUML = maketrans(BASE64_ALPHABET.encode(PLANT_UML_SERVER_ENCODING),
                            PLANTUML_ALPHABET.encode(PLANT_UML_SERVER_ENCODING))

def encode(plantuml_text):
    """zlib compress the plantuml text and encode it for the plantuml server.
    """
    zlibbed_str = compress(plantuml_text.encode(PLANT_UML_SERVER_ENCODING))
    compressed_string = zlibbed_str[2:-4]
    return base64.b64encode(
        compressed_string).translate(
            B64_TO_PLANTUML).decode(
                PLANT_UML_SERVER_ENCODING)
