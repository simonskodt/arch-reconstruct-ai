"""Guardrails to enforce workspace boundaries on navigation and file management functions."""
import os
from typing import Callable, Any
from functools import wraps
from src.agent.tools.navigation.config import AGENT_WORKSPACE_BASE_PATH
from src.agent.tools.navigation.util import normalize_path

def enforce_workspace_boundary(func: Callable) -> Callable:
    """
    Decorator that enforces workspace boundaries on navigation and file management functions.

    If the operation would take the agent outside the workspace,
    it fails and returns the agent to the workspace root.
    """
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        try:
            # Check we are in the workspacebefore executing the function
            if (error_msg := _reset_to_workspace_root_if_outside()):
                return error_msg

            # Execute the function
            result = func(*args, **kwargs)

            # Check we are in the workspace again after execution
            if (error_msg := _reset_to_workspace_root_if_outside()):
                return error_msg
            return result

        except Exception as e:
            # On any error, ensure we're in a safe location
            try:
                if (error_msg := _reset_to_workspace_root_if_outside()):
                    return error_msg
            except Exception:
                pass
            return f"Error: {e}"

    return wrapper

def _reset_to_workspace_root_if_outside() -> str | None:
    error_message = f"Error: Operation is outside the agent workspace. \
    Returned to root: {AGENT_WORKSPACE_BASE_PATH}"
    current_dir = os.getcwd()
    if not _is_within_workspace(current_dir):
        os.chdir(AGENT_WORKSPACE_BASE_PATH)
        return error_message
    return None

def _is_within_workspace(path: str) -> bool:
    """Check if path is within the allowed workspace directory."""
    try:
        abs_path = normalize_path(path)
        abs_path.relative_to(AGENT_WORKSPACE_BASE_PATH)
        return True

    except ValueError:
        # relative_to raises ValueError if path is not a subpath
        return False
