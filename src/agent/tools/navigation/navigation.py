"""Navigation tools for the agent to interact with the filesystem."""
import os
from pathlib import Path
from typing import List
from dotenv import load_dotenv
from langchain.tools import tool
from src.agent.tools.navigation.config import REPOSITORIES_DIR

load_dotenv()

def _get_workspace_root() -> Path:
    """Get workspace root directory from environment variable."""
    root_dir = os.getenv("AGENT_WORKSPACE_BASE_PATH")
    if not root_dir:
        raise ValueError("AGENT_WORKSPACE_BASE_PATH environment variable is not set")
    return _normalize_path(root_dir)


def _normalize_path(path: str) -> Path:
    """Normalize a path across OSes and WSL/Windows interop."""
    path = str(path).strip()

    # Convert WSL paths (/mnt/c/...) -> Windows (C:\...)
    if path.startswith("/mnt/") and len(path) > 6 and path[5].isalpha() and path[6] == "/":
        drive = path[5].upper()
        rest = path[7:]
        path = f"{drive}:/{rest}"

    # Convert Git Bash /c/... -> Windows C:/...
    elif path.startswith("/") and len(path) > 2 and path[1].isalpha() and path[2] == "/":
        drive = path[1].upper()
        rest = path[3:]
        path = f"{drive}:/{rest}"

    return Path(path).resolve()


def _is_within_workspace(path: str) -> bool:
    """Check if path is within the allowed workspace directory."""
    try:
        workspace_root = _get_workspace_root()
        abs_path = _normalize_path(path)

        # Allow access to workspace root and its subdirectories
        abs_path.relative_to(workspace_root)
        return True
    except ValueError:
        # relative_to raises ValueError if path is not a subpath
        return False


def _resolve_repository_path(repo_name: str) -> Path:
    """Get the full path to a repository by name."""
    repository_root = (_get_workspace_root() / REPOSITORIES_DIR).resolve()

    if repo_name and repo_name.strip():
        return _normalize_path(str(repository_root / repo_name))

    return repository_root


@tool("list_directory")
def list_directory() -> List[str]:
    """List all files and directories in the current working directory."""
    try:
        return os.listdir(".")
    except OSError as e:
        return [f"Error listing directory: {e}"]


@tool("get_current_directory")
def get_current_directory() -> str:
    """Return the current working directory path."""
    return os.getcwd()


@tool("change_directory")
def change_directory(path: str) -> str:
    """Change the current working directory with path resolution and safety checks.

    Supports absolute paths, relative paths, and repository names.
    """
    try:
        current_dir = Path.cwd()

        # Resolve the target path
        if Path(path).is_absolute():
            target_path = Path(path)
        elif path.startswith(("./", "../")):
            target_path = (current_dir / path).resolve()
        else:
            # Try as repository name first, then as relative path
            repo_path = _resolve_repository_path(path)
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

    except Exception as e:
        return f"Error changing directory: {e}"


@tool("navigate_to_repository")
def navigate_to_repository(repo_name: str) -> str:
    """Navigate directly to a specific repository in the workspace."""
    try:
        repo_path = _resolve_repository_path(repo_name)

        if not repo_path.exists():
            return f"Error: Repository '{repo_name}' not found at {repo_path}"

        if not repo_path.is_dir():
            return f"Error: '{repo_path}' is not a directory"

        os.chdir(repo_path)
        return f"Successfully navigated to repository: {os.getcwd()}"

    except Exception as e:
        return f"Error navigating to repository: {e}"


@tool("list_repositories")
def list_repositories() -> str:
    """List all available repositories in the workspace."""
    try:
        repository_root = (_get_workspace_root() / REPOSITORIES_DIR).resolve()

        if not repository_root.exists():
            return f"Error: Workspace root not found at {repository_root}"

        repos = [
            item.name for item in repository_root.iterdir()
            if item.is_dir() and not item.name.startswith('.')
        ]

        if repos:
            return f"Available repositories: {', '.join(sorted(repos))}"
        return "No repositories found in workspace."

    except Exception as e:
        return f"Error listing repositories: {e}"
