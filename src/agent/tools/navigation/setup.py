"""Ensure directories exist for agent operations."""
import os
from pathlib import Path
from dotenv import load_dotenv
from langchain.tools import tool
from .config import REQUIRED_DIRS

@tool("setup_directories")
def setup_directories(
    path_name: str = "agent_workspace",
    required_dirs: list[str] | None = None
) -> dict[str, list[str]]:
    """Ensure necessary directories exist."""

    if required_dirs is None:
        required_dirs = REQUIRED_DIRS

    created_dirs = []
    for dir_name in required_dirs:
        dir_path = Path(path_name) / dir_name
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)
            created_dirs.append(str(dir_path))

    return {"created": created_dirs}

@tool("create_directory_in_root")
def create_directory_in_root(dirname: str = "agent_workspace") -> str:
    """Create a directory at the workspace base path (if dirname matches base) or within it.

    If AGENT_WORKSPACE_BASE_PATH already ends with the directory name you want to create,
    this will create the base path directly without duplication.
    """
    load_dotenv()

    root_dir = os.getenv("AGENT_WORKSPACE_BASE_PATH")
    if root_dir is None:
        raise ValueError("AGENT_WORKSPACE_BASE_PATH environment variable is not set")

    base_path = Path(root_dir).resolve()

    # Check if the base path already ends with the dirname
    # e.g., if AGENT_WORKSPACE_BASE_PATH = "arch-reconstruct-ai/agent-workspace"
    # and dirname = "agent_workspace" or "agent-workspace"
    if base_path.name == dirname or base_path.name == dirname.replace('_', '-'):
        target_dir = base_path
    else:
        # Create as a subdirectory of the base path
        target_dir = base_path / dirname

    # Check if it already exists
    if target_dir.exists():
        if target_dir.is_dir():
            return f"Directory already exists at {target_dir}"
        return f"Error: Path exists but is not a directory: {target_dir}"

    # Create the directory
    target_dir.mkdir(parents=True, exist_ok=True)

    return f"Successfully created directory at {target_dir}"
