"""Unit tests for file management functions."""
import tempfile
from unittest.mock import patch
from pathlib import Path

from src.agent.tools.navigation.file_management import read_file
from src.agent.tools.navigation.config import AGENT_WORKSPACE_BASE_PATH


class TestFileManagement:
    """Test file management functions."""

    def test_read_file_successful(self):
        """Test successful file reading."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "test.txt"
            test_content = "Hello, World!\nThis is a test file."
            test_file.write_text(test_content)

            # Mock workspace boundary checks
            with patch('src.agent.tools.navigation.guardrails.'
                       '_reset_to_workspace_root_if_outside',
                       return_value=None):
                result = read_file.invoke({"file_path": str(test_file)})

                assert result == test_content

    def test_read_file_not_found(self):
        """Test reading nonexistent file."""
        nonexistent_path = "/nonexistent/file.txt"

        # Mock workspace boundary checks
        with patch('src.agent.tools.navigation.guardrails.'
                   '_reset_to_workspace_root_if_outside',
                   return_value=None):
            result = read_file.invoke({"file_path": nonexistent_path})

            assert "Error reading file" in result
            assert nonexistent_path in result

    def test_read_file_outside_workspace(self):
        """Test reading file outside workspace."""
        outside_path = str(AGENT_WORKSPACE_BASE_PATH.parent / "outside.txt")

        result = read_file.invoke({"file_path": outside_path})

        # The guardrails decorator blocks this at the decorator level
        assert "Operation is outside the agent workspace" in result
