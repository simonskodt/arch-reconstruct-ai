"""Unit tests for GitHub-related functions."""
import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest

from src.agent.tools.github import git_clone_tool


@pytest.fixture(autouse=True)
def mock_workspace_env():
    """Fixture that mocks the required AGENT_WORKSPACE_BASE_PATH environment variable."""
    with patch.dict(os.environ, {"AGENT_WORKSPACE_BASE_PATH": "/tmp/test_workspace"}):
        yield

@pytest.mark.parametrize(
    "repo_url, dest, expected_dest_suffix, branch",
    [
        ("https://github.com/user/repo.git", "test_repo", "test_repo", "main"),
        ("https://github.com/user/another-repo.git", "another_repo", "another_repo", "master"),
    ]
)
def test_git_clone_creates_repository_at_destination_based_on_url(repo_url,
                                                                  dest,
                                                                  expected_dest_suffix,
                                                                  branch):
    """Test successful git clone operation."""
    with tempfile.TemporaryDirectory() as temp_dir:
        repo_dir = Path(temp_dir) / "repositories"
        with patch('os.getcwd', return_value=temp_dir), \
             patch('os.makedirs') as mock_makedirs, \
             patch('os.path.exists', return_value=False), \
             patch('git.Repo.clone_from') as mock_clone, \
             patch('src.agent.tools.github._resolve_repository_path', return_value=str(repo_dir)):

            # Mock the repo object
            mock_repo = MagicMock()
            mock_repo.active_branch.name = branch
            mock_repo.head.is_detached = False
            mock_clone.return_value = mock_repo

            result = git_clone_tool.invoke({
                "repo_url": repo_url,
                "dest": dest
            })

            assert result["success"] is True
            assert expected_dest_suffix in result["dest"]
            assert result["branch"] == branch
            assert result["error"] is None
            mock_clone.assert_called_once()

            destination = repo_dir / dest
            mock_makedirs.assert_called_with(destination, exist_ok=True)


def test_git_clone_destination_exists_no_overwrite():
    """Test git clone when destination exists and overwrite is False."""
    with tempfile.TemporaryDirectory() as temp_dir:
        repo_dir = Path(temp_dir) / "repositories"
        existing_repo_path = repo_dir / "existing_repo"
        existing_repo_path.mkdir(parents=True, exist_ok=True)  # Create the directory

        with patch('os.getcwd', return_value=temp_dir), \
             patch('src.agent.tools.github._resolve_repository_path', return_value=str(repo_dir)):

            result = git_clone_tool.invoke({
                "repo_url": "https://github.com/user/repo.git",
                "dest": "existing_repo",
                "overwrite": False
            })

            assert result["success"] is False
            assert "already exists" in result["error"]


def test_git_clone_destination_exists_with_overwrite():
    """Test git clone when destination exists and overwrite is True."""
    with tempfile.TemporaryDirectory() as temp_dir:
        repo_dir = Path(temp_dir) / "repositories"
        existing_repo_path = repo_dir / "existing_repo"
        existing_repo_path.mkdir(parents=True, exist_ok=True)  # Create the directory

        with patch('os.getcwd', return_value=temp_dir), \
             patch('os.makedirs') as mock_makedirs, \
             patch('shutil.rmtree') as mock_rmtree, \
             patch('git.Repo.clone_from') as mock_clone, \
             patch('src.agent.tools.github._resolve_repository_path', return_value=str(repo_dir)):

            # Mock the repo object
            mock_repo = MagicMock()
            mock_repo.active_branch.name = "main"
            mock_repo.head.is_detached = False
            mock_clone.return_value = mock_repo

            result = git_clone_tool.invoke({
                "repo_url": "https://github.com/user/repo.git",
                "dest": "existing_repo",
                "overwrite": True
            })

            assert result["success"] is True
            mock_rmtree.assert_called_once_with(existing_repo_path)
            mock_clone.assert_called_once()
            destination = repo_dir / "existing_repo"
            mock_makedirs.assert_called_with(destination, exist_ok=True)
