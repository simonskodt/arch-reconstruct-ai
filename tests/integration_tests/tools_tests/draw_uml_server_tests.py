"""Integration tests for UML drawing tool functions. that interact with the UML drawing server."""
import os
from typing import get_args
import tempfile
import time
import subprocess
import requests
import pytest
from dotenv import load_dotenv

from src.agent.tools.drawing.config import ExportFormats, SUCCESS_STATUS_CODE, PLANT_UML_SERVER_URL
from src.agent.tools.drawing.draw_uml import (
    create_uml_diagram,
    export_uml,
    update_uml,
    _validate_uml,
    _export_uml
)

@pytest.fixture(scope="session", autouse=True)
def ensure_plantuml_server():
    """Ensure PlantUML server is running before tests."""
    server_url = PLANT_UML_SERVER_URL
    load_dotenv()
    skip = os.getenv("PLANTUML_INTEGRATION_TESTS")
    if skip is None or skip.lower() != 'true':
        pytest.skip("PlantUML tests skipped")

    def is_server_running():
        try:
            response = requests.get(f"{server_url}/", timeout=5)
            return response.status_code == 200
        except Exception as _:
            return False

    # Check if server is already running
    if is_server_running():
        return

    # Try to start the server using Docker
    try:
        # Check if container exists but is stopped
        result = subprocess.run(
            ["docker", "ps", "-a", "--filter", "name=plantumlserver", "--format", "{{.Names}}"],
            capture_output=True, text=True, timeout=10, check=True)

        if "plantumlserver" in result.stdout:
            # Container exists, try to start it
            print("Starting existing PlantUML container...")
            subprocess.run(
                ["docker", "start", "plantumlserver"],
                check=True, timeout=30
            )
        else:
            # Container doesn't exist, create and run it
            print("Creating and starting new PlantUML container...")
            subprocess.run([
                "docker", "run", "-d", "-p", "8080:8080",
                "--name", "plantumlserver", "plantuml/plantuml-server:jetty"
            ], check=True, timeout=60)

        # Wait for server to be ready
        for _ in range(30):
            if is_server_running():
                return
            time.sleep(1)
        pytest.fail("PlantUML server failed to start within 30 seconds")

    except subprocess.CalledProcessError as e:
        pytest.fail(f"Failed to start PlantUML server: {e}")
    except FileNotFoundError:
        pytest.fail("Docker not found. Please install Docker and run: " \
        "docker run -d -p 8080:8080 --name plantumlserver plantuml/plantuml-server:jetty")


# Test data for parameterized tests
UML_CONTENTS = [
    # Basic sequence diagram
    ("@startuml Basic\nAlice -> Bob: Hello\nBob --> Alice: Hi\n@enduml",
     "basic_sequence"),

    # Class diagram
    ("@startuml Class\nclass User {\n  +name: String\n  +login()\n}\n@enduml",
     "class_diagram"),

    # Activity diagram
    ("@startuml Activity\nstart\n:Action 1;\nif (condition) then (yes)\n  \
     :Action 2;\nelse (no)\n  :Action 3;\nendif\nstop\n@enduml",
     "activity_diagram"),

    # Use case diagram
    ("@startuml UseCase\n:User: --> (Login)\n:User: --> (View Profile)\n@enduml",
     "use_case_diagram"),
]

@pytest.mark.parametrize("uml_content, diagram_type", UML_CONTENTS)
def test_create_uml_saves_file_to_path(uml_content, diagram_type):
    """Test creating a valid UML diagram with different content types."""
    with tempfile.TemporaryDirectory() as temp_dir:
        name = f"Test {diagram_type.replace('_', ' ').title()}"
        save_path = os.path.join(temp_dir, f"test_{diagram_type}.puml")

        # Create UML
        tool_input = {"name": name, "diagram_content": uml_content, "path": save_path}
        result = create_uml_diagram.invoke(tool_input)
        assert result == save_path
        assert os.path.exists(save_path)

def test_create_invalid_uml():
    """Test creating an invalid UML diagram returns an error message."""
    with tempfile.TemporaryDirectory() as temp_dir:
        name = "Test Diagram"
        uml_text_invalid = """@startuml
                            bob -> hello
                            invalid !
                            @enduml"""
        save_path = os.path.join(temp_dir, "test_invalid.puml")

        tool_input = {"name": name, "diagram_content": uml_text_invalid, "path": save_path}
        result = create_uml_diagram.invoke(tool_input)
        assert "Error" in result
        assert not os.path.exists(save_path)  # Should not create file for invalid UML


@pytest.mark.parametrize("uml_content, diagram_type", UML_CONTENTS)
@pytest.mark.parametrize("format_type", get_args(ExportFormats))
def test_export_uml_to_exportable_formats(uml_content, diagram_type, format_type):
    """Test exporting UML to different formats with various content types."""
    with tempfile.TemporaryDirectory() as temp_dir:
        save_path = os.path.join(temp_dir, f"test_{diagram_type}.puml")
        output_path = os.path.join(temp_dir, f"test_{diagram_type}.{format_type}")

        # Create UML file
        with open(save_path, 'w', encoding='utf-8') as f:
            f.write(uml_content)

        # Export to the specified format
        export_input = {"file_path": save_path,
                        "output_path": output_path,
                        "format_type": format_type}
        export_result = export_uml.invoke(export_input)
        assert export_result == output_path
        assert os.path.exists(output_path)

@pytest.mark.parametrize("uml_content, _", UML_CONTENTS)
@pytest.mark.parametrize("format_type", get_args(ExportFormats))
def test_export_uml_in_memory(uml_content, _, format_type):
    """Test exporting UML to in-memory content."""

    # Export without output_path (in-memory)
    result = _export_uml(uml_content, format_type=format_type)

    assert isinstance(result, str)
    assert result == SUCCESS_STATUS_CODE
    # If valid, should not contain Error
    assert "Error" not in result

def test_validate_uml_valid():
    """Test validating valid UML."""
    valid_uml = "@startuml\nAlice -> Bob\n@enduml"
    result = _validate_uml(valid_uml)
    assert result is None

def test_validate_uml_invalid_content():
    """Test validating invalid UML."""
    invalid_uml = "@startuml\nAlice Bob Hello\n@enduml"
    result = _validate_uml(invalid_uml)
    assert isinstance(result, str)
    assert "Error" in result

def test_update_uml_valid():
    """Test updating UML with valid content."""
    with tempfile.TemporaryDirectory() as temp_dir:
        initial_content = "@startuml\nAlice -> Bob\n@enduml"
        updated_content = "@startuml\nAlice -> Bob: Hello\n@enduml"
        file_path = os.path.join(temp_dir, "test_update.puml")

        # Create initial file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(initial_content)

        result = update_uml.invoke({"uml_content": updated_content, "file_path": file_path})
        assert result == file_path

        # Check updated content
        with open(file_path, 'r', encoding='utf-8') as f:
            assert f.read() == updated_content

def test_update_uml_invalid():
    """Test updating UML with invalid content reverts to previous."""
    with tempfile.TemporaryDirectory() as temp_dir:
        initial_content = "@startuml\nAlice -> Bob\n@enduml"
        invalid_content = "@startuml\nAlice Bob Hello\n@enduml"
        file_path = os.path.join(temp_dir, "test_update_invalid.puml")

        # Create initial file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(initial_content)

        result = update_uml.invoke({"uml_content": invalid_content, "file_path": file_path})
        assert "Error" in result

        # Check content reverted
        with open(file_path, 'r', encoding='utf-8') as f:
            assert f.read() == initial_content
