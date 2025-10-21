"""Unit tests for utility functions."""
import os
from unittest.mock import patch
from pathlib import Path
import pytest

from src.agent.tools.navigation.util import normalize_path, get_workspace_root


class TestUtilFunctions:
    """Test utility functions."""

    @pytest.mark.parametrize("input_path,expected_checks", [
        ("C:\\Users\\test\\file.txt",
         {"is_path": True, "contains": ["C:", "Users", "test", "file.txt"]}),
        ("/mnt/c/Users/test/file.txt",
         {"is_path": True, "contains": ["C:", "Users", "test"]}),
        ("/c/Users/test/file.txt",
         {"is_path": True, "contains": ["C:", "Users", "test"]}),
        ("relative/path", {"is_path": True, "is_absolute": True}),
        ("  /mnt/c/test  ", {"is_path": True, "contains": ["C:", "test"]}),
        ("  ./test/repo  ", {"is_path": True, "contains": ["C:", "test", "repo"]}),

    ], ids=["windows_path", "wsl_path", "git_bash_path", "relative_path",
            "whitespace_path", "dot_slash_path"])
    def test_normalize_path_various_inputs(self, input_path, expected_checks):
        """Test normalizing various types of paths."""
        result = normalize_path(input_path)

        assert isinstance(result, Path)

        if "is_absolute" in expected_checks:
            assert result.is_absolute()

        if "contains" in expected_checks:
            result_str = str(result)
            for substring in expected_checks["contains"]:
                assert substring in result_str

    def test_get_workspace_root_successful(self):
        """Test getting workspace root with environment variable set."""
        expected_root = "/test/workspace"
        with patch.dict(os.environ, {"AGENT_WORKSPACE_BASE_PATH": expected_root}):
            result = get_workspace_root()

            assert isinstance(result, Path)
            # The path gets normalized (resolved), so check that the key components are there
            assert "test" in str(result) and "workspace" in str(result)

    def test_get_workspace_root_missing_env_var(self):
        """Test getting workspace root when environment variable is not set."""
        # Remove the env var if it exists
        with patch.dict(os.environ, {}, clear=True), \
             patch('os.getenv', return_value=None):
            try:
                get_workspace_root()
                assert False, "Should have raised ValueError"
            except ValueError as e:
                assert "AGENT_WORKSPACE_BASE_PATH environment variable is not set" in str(e)
