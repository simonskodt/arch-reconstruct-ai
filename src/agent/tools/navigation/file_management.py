"""File management tools for the agent."""
from pathlib import Path
from langchain.tools import tool
from src.agent.tools.navigation.config import AGENT_WORKSPACE_BASE_PATH
from src.agent.tools.navigation.guardrails import enforce_workspace_boundary


def make_directory(dirname: str, path: Path = AGENT_WORKSPACE_BASE_PATH) -> dict[str, str]:
    """
    Core implementation for creating a directory.

    Args:
        dirname: Name of directory to create
        base_path: Base path to create directory in (defaults to AGENT_WORKSPACE_BASE_PATH)

    Returns:
        Dictionary with status, path, and message
    """
    if path is None:
        path = AGENT_WORKSPACE_BASE_PATH

    target_dir = path / dirname
    # Check if directory already exists
    if target_dir.exists():
        if target_dir.is_dir():
            return {
                "status": "exists",
                "path": str(target_dir),
                "message": f"Directory already exists at {target_dir}"
            }

    # Create the directory
    target_dir.mkdir(parents=True, exist_ok=True)
    return {
        "status": "created",
        "path": str(target_dir),
        "message": f"Successfully created directory at {target_dir}"
    }

@tool("read_file")
@enforce_workspace_boundary
def read_file(file_path: str) -> str:
    """Read the contents of a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        return f"Error reading file {file_path}: {e}"
