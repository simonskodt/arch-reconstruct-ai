"""Unit tests for navigation guardrails functions."""
import os
from unittest.mock import patch
from pathlib import Path

from src.agent.tools.navigation.guardrails import (
    _is_within_workspace,
    _reset_to_workspace_root_if_outside,
    enforce_workspace_boundary,
)
from src.agent.tools.navigation.config import AGENT_WORKSPACE_BASE_PATH


class TestWorkspaceBoundaryChecks:
    """Test workspace boundary validation functions."""

    def test_is_within_workspace_valid_path(self):
        """Test _is_within_workspace with a path inside the workspace."""
        # Test with workspace root itself
        assert _is_within_workspace(str(AGENT_WORKSPACE_BASE_PATH))

        # Test with subdirectory
        subdir = AGENT_WORKSPACE_BASE_PATH / "subdir"
        assert _is_within_workspace(str(subdir))

        # Test with nested subdirectory
        nested = AGENT_WORKSPACE_BASE_PATH / "dir1" / "dir2"
        assert _is_within_workspace(str(nested))

    def test_is_within_workspace_invalid_path(self):
        """Test _is_within_workspace with a path outside the workspace."""
        # Test with parent directory
        parent = AGENT_WORKSPACE_BASE_PATH.parent
        assert not _is_within_workspace(str(parent))

        # Test with sibling directory
        sibling = AGENT_WORKSPACE_BASE_PATH.parent / "sibling_dir"
        assert not _is_within_workspace(str(sibling))

        # Test with completely different path
        different = Path("/completely/different/path")
        assert not _is_within_workspace(str(different))

    def test_is_within_workspace_edge_cases(self):
        """Test _is_within_workspace with edge cases."""
        # Test with relative path that resolves inside workspace
        with patch('os.getcwd', return_value=str(AGENT_WORKSPACE_BASE_PATH)):
            # Relative path "." should be within workspace
            assert _is_within_workspace(".")

        # Test with empty string (should resolve to current dir)
        with patch('os.getcwd', return_value=str(AGENT_WORKSPACE_BASE_PATH)):
            assert _is_within_workspace("")

    @patch('os.getcwd')
    @patch('os.chdir')
    def test_reset_to_workspace_root_when_outside(self, mock_chdir, mock_getcwd):
        """Test _reset_to_workspace_root_if_outside when outside workspace."""
        # Mock being outside workspace
        outside_path = str(AGENT_WORKSPACE_BASE_PATH.parent / "outside")
        mock_getcwd.return_value = outside_path

        result = _reset_to_workspace_root_if_outside()

        # Should return error message
        assert result is not None
        assert "Operation is outside the agent workspace" in result
        assert str(AGENT_WORKSPACE_BASE_PATH) in result

        # Should change directory to workspace root
        mock_chdir.assert_called_once_with(AGENT_WORKSPACE_BASE_PATH)

    @patch('os.getcwd')
    @patch('os.chdir')
    def test_reset_to_workspace_root_when_inside(self, mock_chdir, mock_getcwd):
        """Test _reset_to_workspace_root_if_outside when inside workspace."""
        # Mock being inside workspace
        inside_path = str(AGENT_WORKSPACE_BASE_PATH / "inside")
        mock_getcwd.return_value = inside_path

        result = _reset_to_workspace_root_if_outside()

        # Should return None (no error)
        assert result is None

        # Should not change directory
        mock_chdir.assert_not_called()


class TestEnforceWorkspaceBoundaryDecorator:
    """Test the enforce_workspace_boundary decorator."""

    def test_decorator_allows_operation_inside_workspace(self):
        """Test decorator allows function execution when inside workspace."""
        @enforce_workspace_boundary
        def dummy_function():
            return "success"

        with patch('os.getcwd', return_value=str(AGENT_WORKSPACE_BASE_PATH)):
            result = dummy_function()
            assert result == "success"

    def test_decorator_blocks_operation_outside_workspace(self):
        """Test decorator blocks function execution when outside workspace."""
        @enforce_workspace_boundary
        def dummy_function():
            return "should not execute"

        outside_path = str(AGENT_WORKSPACE_BASE_PATH.parent / "outside")

        with patch('os.getcwd', return_value=outside_path), \
             patch('os.chdir') as mock_chdir:

            result = dummy_function()

            # Should return error message
            assert isinstance(result, str)
            assert "Operation is outside the agent workspace" in result

            # Should reset to workspace root
            mock_chdir.assert_called_with(AGENT_WORKSPACE_BASE_PATH)

    def test_decorator_blocks_after_execution_outside_workspace(self):
        """Test decorator blocks when function execution takes us outside workspace."""
        @enforce_workspace_boundary
        def function_that_changes_dir():
            # Simulate function that changes to outside directory
            outside_path = str(AGENT_WORKSPACE_BASE_PATH.parent / "outside")
            os.chdir(outside_path)
            return "executed"

        with patch('os.getcwd', return_value=str(AGENT_WORKSPACE_BASE_PATH)), \
             patch('os.chdir') as mock_chdir:

            # First call to getcwd returns workspace path (before execution)
            # Second call returns outside path (after execution)
            mock_chdir.side_effect = lambda path: None

            # Mock the post-execution check to find us outside
            with patch('src.agent.tools.navigation.guardrails._reset_to_workspace_root_if_outside')\
            as mock_reset:
                mock_reset.return_value = "Error: Operation is outside the agent workspace"

                result = function_that_changes_dir()

                # Should return error message from post-execution check
                assert "Operation is outside the agent workspace" in result

    def test_decorator_handles_function_exceptions(self):
        """Test decorator handles exceptions in decorated function."""
        @enforce_workspace_boundary
        def failing_function():
            raise ValueError("Test error")

        with patch('os.getcwd', return_value=str(AGENT_WORKSPACE_BASE_PATH)):
            result = failing_function()

            # Should return error message
            assert isinstance(result, str)
            assert "Error: Test error" in result
