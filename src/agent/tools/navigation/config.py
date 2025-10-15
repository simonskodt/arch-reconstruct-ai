"""Constants and configurations for the agent tools."""
from .util import get_workspace_root

REPOSITORIES_DIR = "repositories"

TEMP_DIR = f"temp/{REPOSITORIES_DIR}"
LOGS_DIR = "logs"

REQUIRED_DIRS = [
    REPOSITORIES_DIR,
    TEMP_DIR,
    LOGS_DIR
]

AGENT_WORKSPACE_BASE_PATH = get_workspace_root()
