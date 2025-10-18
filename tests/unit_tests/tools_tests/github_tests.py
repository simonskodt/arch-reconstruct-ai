"""Unit tests for GitHub-related functions."""
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest

from src.agent.tools.github import git_clone_tool

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
        with patch('os.getcwd', return_value=temp_dir), \
             patch('os.makedirs') as mock_makedirs, \
             patch('os.path.exists', return_value=False), \
             patch('git.Repo.clone_from') as mock_clone:

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

            destination = str(Path(f"{temp_dir}/repositories/{dest}").resolve())
            mock_makedirs.assert_called_with(destination, exist_ok=True)


def test_git_clone_destination_exists_no_overwrite():
    """Test git clone when destination exists and overwrite is False."""
    with tempfile.TemporaryDirectory() as temp_dir:
        with patch('os.getcwd', return_value=temp_dir), \
             patch('os.path.exists', return_value=True):

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
        with patch('os.getcwd', return_value=temp_dir), \
             patch('os.makedirs') as mock_makedirs, \
             patch('os.path.exists', return_value=True), \
             patch('shutil.rmtree') as mock_rmtree, \
             patch('git.Repo.clone_from') as mock_clone:

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
            mock_rmtree.assert_called_once()
            mock_clone.assert_called_once()
            destination = str(Path(f"{temp_dir}/repositories/existing_repo").resolve())
            mock_makedirs.assert_called_with(destination, exist_ok=True)
