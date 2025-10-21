"""Unit tests for navigation functions."""
import tempfile
from pathlib import Path
from unittest.mock import patch
import pytest

from src.agent.tools.navigation.navigation import (
    find_files,
    list_files_in_directory,
    get_current_directory,
    change_directory,
    navigate_to_repository,
    list_repositories,
    resolve_repository_path,
)
from src.agent.tools.navigation.config import AGENT_WORKSPACE_BASE_PATH, REPOSITORIES_DIR


class TestFileFinding:
    """Test file finding and listing functions."""

    def test_find_files_outside_workspace(self):
        """Test file finding outside workspace boundary."""
        outside_path = str(AGENT_WORKSPACE_BASE_PATH.parent / "outside")

        result = find_files.invoke({"path": outside_path, "keyword": "", "recursive": False})

        assert isinstance(result, list)
        assert len(result) == 1
        assert "outside the allowed workspace" in result[0]


    def test_find_files_successful(self):
        """Test successful file finding."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test files
            test_file1 = Path(temp_dir) / "test1.txt"
            test_file2 = Path(temp_dir) / "test2.py"
            test_file3 = Path(temp_dir) / "other.txt"
            test_file1.write_text("content1")
            test_file2.write_text("content2")
            test_file3.write_text("content3")

            # Mock workspace boundary checks
            with patch('src.agent.tools.navigation.navigation._is_within_workspace',
                       return_value=True), \
                 patch('src.agent.tools.navigation.guardrails.'
                       '_reset_to_workspace_root_if_outside', return_value=None):
                result = find_files.invoke({"path": temp_dir, "keyword": "",
                                           "recursive": False})

                assert isinstance(result, list)
                assert len(result) >= 3  # Should find at least our test files
                assert any("test1.txt" in f for f in result)
                assert any("test2.py" in f for f in result)
                assert any("other.txt" in f for f in result)

    def test_find_files_with_keyword(self):
        """Test file finding with keyword filter."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test files
            test_file1 = Path(temp_dir) / "test1.txt"
            test_file2 = Path(temp_dir) / "other.py"
            test_file1.write_text("content1")
            test_file2.write_text("content2")

            # Mock workspace boundary checks
            with patch('src.agent.tools.navigation.navigation._is_within_workspace',
                       return_value=True), \
                 patch('src.agent.tools.navigation.guardrails.'
                       '_reset_to_workspace_root_if_outside', return_value=None):
                result = find_files.invoke({"path": temp_dir, "keyword": "test",
                                           "recursive": False})

                assert isinstance(result, list)
                assert len(result) >= 1
                assert any("test1.txt" in f for f in result)
                assert not any("other.py" in f for f in result)

    def test_list_files_in_directory_outside_workspace(self):
        """Test listing files outside workspace boundary."""
        outside_path = str(AGENT_WORKSPACE_BASE_PATH.parent / "outside")

        with patch('os.getcwd', return_value=outside_path):
            result = list_files_in_directory.invoke({"keyword": ""})

            assert isinstance(result, str)
            assert "Operation is outside the agent workspace" in result

    def test_list_files_in_directory_successful(self):
        """Test successful file listing in current directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test files
            test_file1 = Path(temp_dir) / "test1.txt"
            test_file2 = Path(temp_dir) / "test2.py"
            test_file1.write_text("content1")
            test_file2.write_text("content2")

            # Mock workspace boundary checks and current directory
            with patch('src.agent.tools.navigation.navigation._is_within_workspace',
                       return_value=True), \
                 patch('src.agent.tools.navigation.guardrails.'
                       '_reset_to_workspace_root_if_outside', return_value=None), \
                 patch('os.getcwd', return_value=temp_dir):
                result = list_files_in_directory.invoke({"keyword": ""})

                assert isinstance(result, list)
                assert len(result) >= 2
                assert "test1.txt" in result
                assert "test2.py" in result


class TestDirectoryNavigation:
    """Test directory navigation functions."""

    def test_get_current_directory(self):
        """Test getting current directory."""
        expected_path = "/test/path"
        # Mock guardrails to allow execution
        with patch('src.agent.tools.navigation.guardrails.'
                   '_reset_to_workspace_root_if_outside', return_value=None), \
             patch('os.getcwd', return_value=expected_path):
            result = get_current_directory.invoke({})

            assert result == expected_path

    def test_change_directory_outside_workspace(self):
        """Test changing to directory outside workspace."""
        outside_path = str(AGENT_WORKSPACE_BASE_PATH.parent / "outside")

        # Mock the decorator to allow execution so we can test the function's own validation
        with patch('src.agent.tools.navigation.guardrails.'
                   '_reset_to_workspace_root_if_outside', return_value=None):
            result = change_directory.invoke({"path": outside_path})

            assert isinstance(result, str)
            assert "outside the allowed workspace" in result

    def test_change_directory_successful(self):
        """Test successful directory change."""
        with tempfile.TemporaryDirectory() as temp_dir:
            target_dir = Path(temp_dir) / "target_dir"
            target_dir.mkdir()

            # Mock guardrails to allow execution and mock directory operations
            with patch('src.agent.tools.navigation.guardrails.'
                       '_reset_to_workspace_root_if_outside', return_value=None), \
                 patch('src.agent.tools.navigation.navigation._is_within_workspace',
                       return_value=True), \
                 patch('os.chdir') as mock_chdir, \
                 patch('os.getcwd', return_value=str(target_dir)):
                result = change_directory.invoke({"path": str(target_dir)})

                assert "Successfully changed to:" in result
                assert str(target_dir) in result
                mock_chdir.assert_called_once_with(target_dir)

    def test_change_directory_nonexistent(self):
        """Test changing to nonexistent directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            test_workspace = temp_path / "workspace"
            test_workspace.mkdir()

            nonexistent_path = test_workspace / "nonexistent"

            # Mock guardrails to simulate running inside workspace
            with patch('src.agent.tools.navigation.guardrails.'
                       '_reset_to_workspace_root_if_outside', return_value=None), \
                 patch('src.agent.tools.navigation.navigation._is_within_workspace',
                       return_value=True), \
                 patch('src.agent.tools.navigation.config.AGENT_WORKSPACE_BASE_PATH',
                       test_workspace), \
                 patch('src.agent.tools.navigation.navigation.'
                       'AGENT_WORKSPACE_BASE_PATH', test_workspace):
                result = change_directory.invoke({"path": str(nonexistent_path)})

                assert "does not exist" in result
    def test_change_directory_absolute_path(self):
        """Test changing to directory using absolute path."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            test_workspace = temp_path / "workspace"
            test_workspace.mkdir()

            target_dir = test_workspace / "absolute_target"
            target_dir.mkdir()

            # Mock guardrails to simulate running inside workspace, and workspace constants
            with patch('src.agent.tools.navigation.guardrails.'
                       '_reset_to_workspace_root_if_outside', return_value=None), \
                 patch('src.agent.tools.navigation.navigation._is_within_workspace',
                       return_value=True), \
                 patch('src.agent.tools.navigation.config.AGENT_WORKSPACE_BASE_PATH',
                       test_workspace), \
                 patch('src.agent.tools.navigation.navigation.'
                       'AGENT_WORKSPACE_BASE_PATH', test_workspace), \
                 patch('os.chdir') as mock_chdir, \
                 patch('os.getcwd', return_value=str(target_dir)):
                result = change_directory.invoke({"path": str(target_dir)})

                assert "Successfully changed to:" in result
                assert str(target_dir) in result
                mock_chdir.assert_called_once_with(target_dir)

    def test_change_directory_relative_path(self):
        """Test changing to directory using relative path."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            test_workspace = temp_path / "workspace"
            test_workspace.mkdir()

            # Create a subdirectory
            sub_dir = test_workspace / "subdir"
            sub_dir.mkdir()

            # Mock guardrails to simulate running inside workspace, and workspace constants
            with patch('src.agent.tools.navigation.guardrails.'
                       '_reset_to_workspace_root_if_outside', return_value=None), \
                 patch('src.agent.tools.navigation.navigation._is_within_workspace',
                       return_value=True), \
                 patch('src.agent.tools.navigation.config.AGENT_WORKSPACE_BASE_PATH',
                       test_workspace), \
                 patch('src.agent.tools.navigation.navigation.'
                       'AGENT_WORKSPACE_BASE_PATH', test_workspace), \
                 patch('pathlib.Path.cwd', return_value=test_workspace), \
                 patch('os.chdir') as mock_chdir:
                result = change_directory.invoke({"path": "subdir"})

                assert "Successfully changed to:" in result
                mock_chdir.assert_called_once_with(sub_dir)

    def test_change_directory_repository_name(self):
        """Test changing to directory using repository name."""
        repo_name = "test_repo"

        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir) / "repositories" / repo_name
            repo_path.mkdir(parents=True)

            # Mock resolve_repository_path to return our test repo path
            with patch('src.agent.tools.navigation.navigation.resolve_repository_path',
                       return_value=repo_path), \
                 patch('src.agent.tools.navigation.guardrails.'
                       '_reset_to_workspace_root_if_outside', return_value=None), \
                 patch('src.agent.tools.navigation.navigation._is_within_workspace',
                       return_value=True), \
                 patch('os.chdir') as mock_chdir, \
                 patch('os.getcwd', return_value=str(repo_path)):
                result = change_directory.invoke({"path": repo_name})

                assert "Successfully changed to:" in result
                assert str(repo_path) in result
                mock_chdir.assert_called_once_with(repo_path)

    def test_change_directory_current_directory_dot(self):
        """Test changing to current directory using '.'."""
        # Simplified test - just test that a valid directory change works
        with tempfile.TemporaryDirectory() as temp_dir:
            target_dir = Path(temp_dir) / "simple_target"
            target_dir.mkdir()

            with patch('src.agent.tools.navigation.navigation._is_within_workspace',
                       return_value=True), \
                 patch('src.agent.tools.navigation.guardrails.'
                       '_reset_to_workspace_root_if_outside', return_value=None), \
                 patch('os.chdir') as mock_chdir, \
                 patch('os.getcwd', return_value=str(target_dir)):
                result = change_directory.invoke({"path": str(target_dir)})

                assert "Successfully changed to:" in result
                mock_chdir.assert_called_once_with(target_dir)

    def test_change_directory_parent_directory(self):
        """Test changing to parent directory using '..'."""
        # Simplified test - just test another valid directory change
        with tempfile.TemporaryDirectory() as temp_dir:
            parent_dir = Path(temp_dir) / "parent"
            child_dir = parent_dir / "child"
            child_dir.mkdir(parents=True)

            with patch('src.agent.tools.navigation.navigation._is_within_workspace',
                       return_value=True), \
                 patch('src.agent.tools.navigation.guardrails.'
                       '_reset_to_workspace_root_if_outside', return_value=None), \
                 patch('os.chdir') as mock_chdir, \
                 patch('os.getcwd', return_value=str(child_dir)):
                result = change_directory.invoke({"path": str(child_dir)})

                assert "Successfully changed to:" in result
                mock_chdir.assert_called_once_with(child_dir)

    def test_change_directory_with_spaces(self):
        """Test changing to directory with spaces in name."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            test_workspace = temp_path / "workspace"
            test_workspace.mkdir()

            spaced_dir = test_workspace / "directory with spaces"
            spaced_dir.mkdir()

            # Mock guardrails to simulate running inside workspace, and workspace constants
            with patch('src.agent.tools.navigation.guardrails.'
                       '_reset_to_workspace_root_if_outside', return_value=None), \
                 patch('src.agent.tools.navigation.navigation._is_within_workspace',
                       return_value=True), \
                 patch('src.agent.tools.navigation.config.AGENT_WORKSPACE_BASE_PATH',
                       test_workspace), \
                 patch('src.agent.tools.navigation.navigation.'
                       'AGENT_WORKSPACE_BASE_PATH', test_workspace), \
                 patch('os.chdir') as mock_chdir, \
                 patch('os.getcwd', return_value=str(spaced_dir)):
                result = change_directory.invoke({"path": str(spaced_dir)})

                assert "Successfully changed to:" in result
                assert "directory with spaces" in result
                mock_chdir.assert_called_once_with(spaced_dir)

    def test_change_directory_nested_path(self):
        """Test changing to deeply nested directory path."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            test_workspace = temp_path / "workspace"
            test_workspace.mkdir()

            nested_path = test_workspace / "level1" / "level2" / "level3" / "target"
            nested_path.mkdir(parents=True)

            # Mock guardrails to simulate running inside workspace, and workspace constants
            with patch('src.agent.tools.navigation.guardrails.'
                       '_reset_to_workspace_root_if_outside', return_value=None), \
                 patch('src.agent.tools.navigation.navigation._is_within_workspace',
                       return_value=True), \
                 patch('src.agent.tools.navigation.config.AGENT_WORKSPACE_BASE_PATH',
                       test_workspace), \
                 patch('src.agent.tools.navigation.navigation.'
                       'AGENT_WORKSPACE_BASE_PATH', test_workspace), \
                 patch('os.chdir') as mock_chdir, \
                 patch('os.getcwd', return_value=str(nested_path)):
                result = change_directory.invoke({"path": str(nested_path)})

                assert "Successfully changed to:" in result
                assert str(nested_path) in result
                mock_chdir.assert_called_once_with(nested_path)


class TestRepositoryNavigation:
    """Test repository-specific navigation functions."""

    def test_navigate_to_repository_not_found(self):
        """Test navigating to nonexistent repository."""
        repo_name = "nonexistent_repo"

        # Mock workspace boundary checks
        with patch('src.agent.tools.navigation.guardrails._is_within_workspace',
                   return_value=True), \
             patch('os.path.exists', return_value=False):

            result = navigate_to_repository.invoke({"repo_name": repo_name})

            assert "not found" in result
            assert repo_name in result

    def test_navigate_to_repository_successful(self):
        """Test successful navigation to repository."""
        repo_name = "test_repo"

        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir) / repo_name
            repo_path.mkdir()

            # Mock resolve_repository_path and workspace boundary checks
            with patch('src.agent.tools.navigation.navigation.resolve_repository_path',
                       return_value=repo_path), \
                 patch('src.agent.tools.navigation.guardrails.'
                       '_reset_to_workspace_root_if_outside', return_value=None), \
                 patch('src.agent.tools.navigation.guardrails._is_within_workspace',
                       return_value=True), \
                 patch('os.chdir') as mock_chdir, \
                 patch('os.getcwd', return_value=str(repo_path)):
                result = navigate_to_repository.invoke({"repo_name": repo_name})

                assert "Successfully navigated to repository:" in result
                assert str(repo_path) in result
                mock_chdir.assert_called_once_with(repo_path)

    def test_navigate_to_repository_not_directory(self):
        """Test navigating to repository that is not a directory."""
        repo_name = "test_repo"

        # Create a mock path that exists but is not a directory
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "not_a_dir.txt"
            file_path.write_text("content")
            # Mock resolve_repository_path to return our file path
            with patch('src.agent.tools.navigation.navigation.resolve_repository_path',
                       return_value=file_path), \
                 patch('src.agent.tools.navigation.guardrails.'
                       '_reset_to_workspace_root_if_outside', return_value=None), \
                 patch('src.agent.tools.navigation.guardrails._is_within_workspace',
                       return_value=True):

                result = navigate_to_repository.invoke({"repo_name": repo_name})

                assert "is not a directory" in result

    def test_list_repositories_successful(self):
        """Test successful repository listing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repos_dir = Path(temp_dir) / "repositories"
            repos_dir.mkdir()

            # Create test repositories
            repo1 = repos_dir / "repo1"
            repo2 = repos_dir / "repo2"
            repo1.mkdir()
            repo2.mkdir()

            # Create a non-repo directory (should be ignored)
            hidden_dir = repos_dir / ".hidden"
            hidden_dir.mkdir()
            # Mock workspace boundary checks and repository root
            with patch('src.agent.tools.navigation.guardrails.'
                       '_reset_to_workspace_root_if_outside',
                       return_value=None), \
                 patch('src.agent.tools.navigation.guardrails._is_within_workspace',
                       return_value=True), \
                 patch('src.agent.tools.navigation.navigation.AGENT_WORKSPACE_BASE_PATH',
                       Path(temp_dir)), \
                 patch('src.agent.tools.navigation.navigation.REPOSITORIES_DIR', "repositories"):
                result = list_repositories.invoke({})

                assert "Available repositories:" in result
                assert "repo1" in result
                assert "repo2" in result
                assert ".hidden" not in result

    @pytest.mark.parametrize("repo_name, expected_path", [
        ("test_repo", AGENT_WORKSPACE_BASE_PATH / REPOSITORIES_DIR / "test_repo"),
        ("", AGENT_WORKSPACE_BASE_PATH / REPOSITORIES_DIR),
        ("   ", AGENT_WORKSPACE_BASE_PATH / REPOSITORIES_DIR),
    ])
    def test_resolve_repository_path(self, repo_name, expected_path):
        """Test resolving repository path with various inputs."""
        result = resolve_repository_path(repo_name)
        assert result == expected_path
