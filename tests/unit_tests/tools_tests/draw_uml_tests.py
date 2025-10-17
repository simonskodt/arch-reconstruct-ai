"""Unit tests for UML drawing tool functions."""
import os
import tempfile
import pytest
from src.agent.tools.drawing.draw_uml import (
    load_uml,
    save_uml,
    _validate_uml,

)

from tests.uml_examples import UML_DIAGRAMS


@pytest.mark.parametrize("uml_content, diagram_type", UML_DIAGRAMS)
def test_save_uml(uml_content, diagram_type):
    """Test saving UML content to a file."""
    with tempfile.TemporaryDirectory() as temp_dir:
        save_path = os.path.join(temp_dir, f"test_{diagram_type}.puml")

        result = save_uml.invoke({"uml_description": uml_content, "file_path": save_path})
        assert result == save_path
        assert os.path.exists(save_path)

        # Check content
        with open(save_path, 'r', encoding='utf-8') as f:
            assert f.read() == uml_content

def test_save_uml_no_overwrite():
    """Test saving UML without overwriting existing file."""
    with tempfile.TemporaryDirectory() as temp_dir:
        file_path = os.path.join(temp_dir, "test_no_overwrite.puml")

        # Create initial file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("initial content")

        # Try to save without overwrite
        result = save_uml.invoke({"uml_description": "new content",
                                  "file_path": file_path,
                                  "overwrite": False})
        assert "already exists" in result
        assert os.path.exists(file_path)

        # Check content unchanged
        with open(file_path, 'r', encoding='utf-8') as f:
            assert f.read() == "initial content"


def test_load_uml():
    """Test loading UML content from a file."""
    with tempfile.TemporaryDirectory() as temp_dir:
        uml_content = "@startuml\nAlice -> Bob\n@enduml"
        file_path = os.path.join(temp_dir, "test_load.puml")

        # Create file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(uml_content)

        result = load_uml.invoke({"file_path": file_path})
        assert result == uml_content

def test_validate_uml_missing_tags():
    """Test validating UML without proper tags."""
    no_tags_uml = "Alice -> Bob"
    result = _validate_uml(no_tags_uml)
    assert isinstance(result, str)
    assert "must start with" in result
