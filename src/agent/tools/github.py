"""
This file defines a tool to clone GitHub repositories using GitPython.
"""
import os
import shutil
from pathlib import Path
from typing import Optional, Dict, Any
from git import Repo, GitCommandError
from git.exc import NoSuchPathError, InvalidGitRepositoryError
from langchain.tools import tool

from src.agent.tools.navigation import _resolve_repository_path

@tool("git_clone")
def git_clone_tool(
    repo_url: str,
    dest: str,
    branch: Optional[str] = None,
    overwrite: bool = False,
) -> Dict[str, Any]:
    """
    Clone a Git repository into ./repositories/{dest}.

    Args:
        repo_url: HTTPS or SSH URL of the repository.
        dest: Name of the destination folder for the clone inside ./repositories/.
        branch: Optional branch to check out.
        overwrite: If True, overwrite existing destination folder.
    Returns:
        A dict with success (bool), dest (str), and error/stdout messages.
    """

    try:
        # Ensure repositories/ root exists
        repo_dir = _resolve_repository_path("")  # Use navigation module to get path

        # Full destination path inside repositories/
        repo_root = Path(repo_dir)
        full_dest = repo_root / dest

        # Handle overwrite
        if full_dest.exists():
            if overwrite:
                # Remove directory or file
                if full_dest.is_dir():
                    shutil.rmtree(full_dest)
                else:
                    full_dest.unlink()
            else:
                return {"success": False, "error": f"Destination {full_dest} already exists."}

        # Clone options
        kwargs = {}
        if branch:
            kwargs["branch"] = branch
            full_dest = f"{full_dest}/{branch}"

        os.makedirs(full_dest, exist_ok=True)
        repo = Repo.clone_from(repo_url, full_dest, **kwargs)

        return {
            "success": True,
            "dest": str(full_dest),
            "branch": repo.active_branch.name if not repo.head.is_detached else "detached",
            "error": None,
        }
    except (GitCommandError, NoSuchPathError, InvalidGitRepositoryError) as e:
        return {"success": False, "dest": str(dest), "error": str(e)}
