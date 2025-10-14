"""Navigation tools for the agent to interact with the filesystem."""
from typing import List
from langchain_core.tools import BaseTool

from .navigation import (
    list_directory,
    get_current_directory,
    change_directory,
    navigate_to_repository,
    list_repositories,
    _resolve_repository_path,
)
from .setup import (
    setup_directories,
    create_directory_in_root,
)


def get_navigation_tools() -> List[BaseTool]:
    """Get all navigation and setup tools.

    Returns:
        List of all navigation tools including:
        - Directory listing and navigation
        - Repository management
        - Directory setup and creation
    """
    return [
        # Navigation tools
        list_directory,
        get_current_directory,
        change_directory,
        navigate_to_repository,
        list_repositories,
        # Setup tools
        setup_directories,
        create_directory_in_root,
    ]


def setup_navigation_workspace() -> dict:
    """Initialize the workspace by creating required directories.

    Returns:
        Dictionary with setup results including created directories
    """
    try:
        # Run the setup to create required directories
        result = setup_directories.invoke({"path_name": "agent_workspace"})
        return {
            "status": "success",
            "message": "Navigation workspace initialized",
            "details": result
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to initialize workspace: {e}",
            "details": {}
        }

setup_navigation_workspace()  # Ensure workspace is set up on import

__all__ = [
    "get_navigation_tools",
    "setup_navigation_workspace",
    "list_directory",
    "get_current_directory",
    "change_directory",
    "navigate_to_repository",
    "list_repositories",
    "setup_directories",
    "create_directory_in_root",
    "_resolve_repository_path",
]
