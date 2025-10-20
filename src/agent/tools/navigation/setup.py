"""Ensure directories exist for agent operations."""
from src.agent.tools.navigation.file_management import make_directory
from src.agent.tools.navigation.config import (
    REQUIRED_DIRS,
    AGENT_WORKSPACE_BASE_PATH,
)

def setup_agent_workspace():
    """Initialize the workspace by creating required directories.

    Returns:
        Dictionary with setup results including created and existing directories
    """
    # Ensure base workspace directory exists using make_directory
    # Pass the parent directory and the workspace name
    agent_root = make_directory(
        dirname=AGENT_WORKSPACE_BASE_PATH.name,
        path=AGENT_WORKSPACE_BASE_PATH.parent
    )

    # Create required subdirectories
    dirs_result = {"created": [], "existing": []}
    for dir_name in REQUIRED_DIRS:
        result = make_directory(dir_name)
        try:
            if result["status"] == "created":
                dirs_result["created"].append(result["path"])
            elif result["status"] == "exists":
                dirs_result["existing"].append(result["path"])
        # pylint: disable=broad-exception-caught
        except Exception as e:
            print(f"Result was: {result}")
            print(f"Error processing directory {dir_name}: {e}")

    return {
        "status": {
            "base_workspace": agent_root,
            "directories": dirs_result
        },
    }
