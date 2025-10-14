"""Constants and configurations for the agent tools."""
from pathlib import Path

# Get the project root (parent of src directory)
# from src/agent/tools/navigation/config.py -> src
SRC_PATH = Path(__file__).resolve().parent.parent.parent
PROJECT_ROOT = SRC_PATH.parent  # -> project_root

REPOSITORIES_DIR = "repositories"
TEMP_DIR = f"temp/{REPOSITORIES_DIR}"
LOGS_DIR = "logs"

REQUIRED_DIRS = [
    REPOSITORIES_DIR,
    TEMP_DIR,
    LOGS_DIR
]
