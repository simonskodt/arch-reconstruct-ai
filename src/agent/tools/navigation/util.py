"""Utility functions for path normalization and environment variable handling."""
import os
from pathlib import Path
from dotenv import load_dotenv

def normalize_path(path: str) -> Path:
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

def get_workspace_root() -> Path:
    """Get workspace root directory from environment variable."""
    load_dotenv()

    root_dir = os.getenv("AGENT_WORKSPACE_BASE_PATH")
    if not root_dir:
        raise ValueError("AGENT_WORKSPACE_BASE_PATH environment variable is not set")
    return normalize_path(root_dir)
