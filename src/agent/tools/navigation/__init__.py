"""
src.agent.tools.navigation - provides tools for the agent to navigate the filesystem,
and to interact with the filesystem.
"""
from typing import List
from langchain_core.tools import BaseTool
from . import config # Import config first to initialize constants
from .navigation import (
    list_files_in_directory,
    find_files,
    get_current_directory,
    change_directory,
    navigate_to_repository,
    list_repositories,
    _resolve_repository_path,
)

from .file_management import (
    read_file,
)
from .setup import setup_agent_workspace


def get_navigation_tools() -> List[BaseTool]:
    """Get all navigation and setup tools.

    Returns:
        List of all navigation tools including
    """
    return [
        list_files_in_directory,
        find_files,
        get_current_directory,
        change_directory,
        navigate_to_repository,
        list_repositories,
    ]
def get_file_management_tools() -> List[BaseTool]:
    """Get all file management and setup tools.

    Returns:
        List of all file management tools including
        - File reading
    """
    return [
        read_file,
    ]

# Ensure required directories exist at import time
setup_agent_workspace()

__all__ = [
    "get_navigation_tools",
    "get_file_management_tools",
    "list_files_in_directory",
    "find_files",
    "get_current_directory",
    "change_directory",
    "navigate_to_repository",
    "list_repositories",
    "_resolve_repository_path",
    "read_file",
]
