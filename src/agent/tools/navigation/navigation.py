"""Navigation tools for the agent to interact with the filesystem."""
import os
from pathlib import Path
from typing import List
from langchain.tools import tool
from src.agent.tools.navigation.util import normalize_path
from src.agent.tools.navigation.config import (REPOSITORIES_DIR, AGENT_WORKSPACE_BASE_PATH,)
from src.agent.tools.navigation.guardrails import enforce_workspace_boundary, _is_within_workspace


@tool("find_files")
@enforce_workspace_boundary
def find_files(path: str = ".", keyword: str = "", recursive: bool = True) -> List[str]:
    """
    Find all files from the given path (default cwd), filtering optionally by keyword.

    Args:
        path: Starting path for search (default is current directory)
        keyword: Optional keyword to filter filenames
        recursive: If True, search recursively; if False, only search immediate directory
    """
    return _find_files(path=path, keyword=keyword, recursive=recursive)


@tool("list_files_in_directory")
@enforce_workspace_boundary
def list_files_in_directory(keyword: str = "") -> List[str]:
    """
    List all files in the current working directory, filtering optionally by keyword.

    This is a convenience wrapper around the file finding logic.
    """
    result = _find_files(path=".", keyword=keyword, recursive=False)
    if isinstance(result, list) and result and not result[0].startswith("Error:"):
        return [os.path.basename(f) for f in result]
    return result

def _find_files(path: str = ".", keyword: str = "", recursive: bool = True) -> List[str]:
    """
    Core implementation for finding files.

    Args:
        path: Starting path for search (default is current directory)
        keyword: Optional keyword to filter filenames
        recursive: If True, search recursively; if False, only search immediate directory
    """
    try:
        start_path = normalize_path(path)

        if not _is_within_workspace(str(start_path)):
            return [f"Error: Path '{path}' is outside the allowed workspace"]

        if not start_path.exists():
            return [f"Error: Path '{path}' does not exist"]

        if not start_path.is_dir():
            return [f"Error: '{path}' is not a directory"]

        files = []

        if recursive:
            # Recursive search using os.walk
            for root, _, files_in_dir in os.walk(start_path):
                # Skip .langgraph_api directory
                if ".langgraph_api" in root:
                    continue
                for file in files_in_dir:
                    if not keyword or keyword.strip() == "" or keyword in file:
                        files.append(os.path.join(root, file))
        else:
            # Non-recursive search - only current directory
            dir_items = os.listdir(start_path)
            no_filter = not keyword or keyword.strip() == ""
            files = [
                str(start_path / item) for item in dir_items
                if item != ".langgraph_api"
                and (no_filter or keyword in item)
                and (start_path / item).is_file()
            ]

        return files
    except OSError as e:
        return [f"Error finding files: {e}"]


@tool("get_current_directory")
@enforce_workspace_boundary
def get_current_directory() -> str:
    """Return the current working directory path."""
    return os.getcwd()


@tool("change_directory")
@enforce_workspace_boundary
def change_directory(path: str) -> str:
    """Change the current working directory with path resolution and safety checks.

    Supports absolute paths, relative paths, and repository names.
    """
    try:
        current_dir = Path.cwd()

        # Resolve the target path
        if Path(path).is_absolute():
            target_path = Path(path)
        else:
            repo_path = resolve_repository_path(path)
            if repo_path.exists():
                target_path = repo_path
            else:
                target_path = (current_dir / path).resolve()

        # Security check
        if not _is_within_workspace(str(target_path)):
            return f"Error: Access to '{target_path}' is outside the allowed workspace"

        # Existence and type checks
        if not target_path.exists():
            return f"Error: Path '{target_path}' does not exist"

        if not target_path.is_dir():
            return f"Error: '{target_path}' is not a directory"

        # Change directory
        os.chdir(target_path)
        return f"Successfully changed to: {os.getcwd()}"
    # pylint: disable=broad-exception-caught
    except Exception as e:
        return f"Error changing directory: {e}"


@tool("navigate_to_repository")
@enforce_workspace_boundary
def navigate_to_repository(repo_name: str) -> str:
    """Navigate directly to a specific repository in the workspace."""
    try:
        repo_path = resolve_repository_path(repo_name)

        if not repo_path.exists():
            return f"Error: Repository '{repo_name}' not found at {repo_path}"

        if not repo_path.is_dir():
            return f"Error: '{repo_path}' is not a directory"

        os.chdir(repo_path)
        return f"Successfully navigated to repository: {os.getcwd()}"
    # pylint: disable=broad-exception-caught
    except Exception as e:
        return f"Error navigating to repository: {e}"


@tool("list_repositories")
@enforce_workspace_boundary
def list_repositories() -> str:
    """List all available repositories in the workspace."""
    try:
        repository_root = (AGENT_WORKSPACE_BASE_PATH / REPOSITORIES_DIR).resolve()

        if not repository_root.exists():
            return f"Error: Workspace root not found at {repository_root}"

        repos = [
            item.name for item in repository_root.iterdir()
            if item.is_dir() and not item.name.startswith('.')
        ]

        if repos:
            return f"Available repositories: {', '.join(sorted(repos))}"
        return "No repositories found in workspace."
    # pylint: disable=broad-exception-caught
    except Exception as e:
        return f"Error listing repositories: {e}"

def resolve_repository_path(repo_name: str) -> Path:
    """Get the full path to a repository by name."""
    repository_root = (AGENT_WORKSPACE_BASE_PATH / REPOSITORIES_DIR).resolve()

    if repo_name and repo_name.strip():
        return normalize_path(str(repository_root / repo_name))

    return repository_root
