"""Unit tests for setup functionality."""
import tempfile
from unittest.mock import patch
from pathlib import Path

from src.agent.tools.navigation.setup import setup_agent_workspace
from src.agent.tools.navigation.config import REQUIRED_DIRS


def test_setup_agent_workspace_successful():
    """Test successful workspace setup when directories don't exist."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        workspace_name = "test_workspace"
        workspace_path = temp_path / workspace_name

        # Mock the workspace base path and make_directory to return expected results
        with patch('src.agent.tools.navigation.setup.AGENT_WORKSPACE_BASE_PATH', workspace_path), \
                patch('src.agent.tools.navigation.config.AGENT_WORKSPACE_BASE_PATH',
                      workspace_path), \
                patch('src.agent.tools.navigation.setup.make_directory') as mock_make_dir:

            # Mock make_directory to return "created" status for new directories
            mock_make_dir.return_value = {
                "status": "created",
                "path": str(workspace_path / "test_dir"),
                "message": "Successfully created directory"
            }

            result = setup_agent_workspace()

            # Check that the function returns the expected structure
            assert "status" in result
            assert "base_workspace" in result["status"]
            assert "directories" in result["status"]

            assert mock_make_dir.call_count == len(REQUIRED_DIRS) + 1  # +1 for base workspace

            # Check that the result contains the created directories
            dirs_result = result["status"]["directories"]
            assert "created" in dirs_result
            assert "existing" in dirs_result

            # Since all directories were "created" by the mock, they should all be in "created"
            assert len(dirs_result["created"]) == len(REQUIRED_DIRS)
            assert len(dirs_result["existing"]) == 0
