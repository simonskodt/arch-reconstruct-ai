"""
This file defines tools to clone GitHub repositories and extract repository details.
"""
import os
import shutil
import json
import asyncio
from pathlib import Path
from typing import Optional, Dict, Any

from git import Repo, GitCommandError
from git.exc import NoSuchPathError, InvalidGitRepositoryError
from langchain.tools import tool
from gitingest.config import MAX_FILE_SIZE

from src.agent.tools.navigation import resolve_repository_path
from .config import GITINGEST_DEFAULT_OUTPUT_LOCATION
from .gitingest_helpers import ingest_local_non_blocking, normalize_path

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
        repo_dir = resolve_repository_path("")  # Use navigation module to get path

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
        return {"success": False, "dest": dest, "error": str(e)}

@tool("extract_git_repository_details_to_file")
async def extract_repository_details(
    local_repository_path: Optional[str],
    output_path: Optional[str] = GITINGEST_DEFAULT_OUTPUT_LOCATION,
) -> Dict[str, Any]:
    """
    Extract and ingest a Git repository (local or remote) into a readable LLM format.

    Args:
        local_repository_path: Path to a local repository directory.
        github_url: HTTPS URL of a remote GitHub repository.
        output_path: Output path for the extraction
            (default: "extract_repository_details.json" (GITINGEST_DEFAULT_OUTPUT_LOCATION),
            use "-" or "stdout" for stdout).
    Returns:
        path to a JSON dict with summary (str), tree (str), and content (str) of the repository.
    """

    try:
        exclude_patterns = {
            "*.pyc",
            "__pycache__",
            ".git",
            ".venv",
            "venv",
            "env",
            "node_modules",
            ".DS_Store",
            "*.log",
            ".pytest_cache",
            "*.egg-info",
            "dist",
            "build",
            "*.lock",
            ".pylintrc"
        }
        # Get current working directory in a non-blocking way
        cwd = await asyncio.to_thread(os.getcwd)
        if local_repository_path is not None:
            path = normalize_path(local_repository_path, cwd)
        else:
            return {
                "success": False,
                "error": "local_repository_path must be provided"
            }

        # Use non-blocking ingest for local repositories
        summary, tree, content = await ingest_local_non_blocking(
            path,
            max_file_size=MAX_FILE_SIZE,
            exclude_patterns=exclude_patterns,
            include_gitignored=False
        )

        extraction = {"summary": summary, "tree": tree, "content": content}

        if output_path in ["-", "stdout"]:
            print(json.dumps(extraction, ensure_ascii=False, indent=2))
            return {"success": True, "data": extraction}

        if output_path is not None:
            # Save the output file in the repository folder
            output_file_path = os.path.join(path, output_path)
            await asyncio.to_thread(
                _write_json_file,
                output_file_path,
                extraction
            )
            return {"success": True, "path": output_file_path}

        return {"success": True, "data": extraction}

    except PermissionError as e:
        return {"success": False, "error": f"Permission denied: {e}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def _write_json_file(file_path: str, data: Dict[str, Any]) -> None:
    """Helper function to write JSON data to a file."""
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


@tool("load_extracted_repository_from_file")
def load_extracted_repository(
    path: str = GITINGEST_DEFAULT_OUTPUT_LOCATION,
    include_summary: bool = True,
    include_tree: bool = True,
    include_content: bool = True
) -> Dict[str, Any]:
    """
    Load the extracted repository details from a file.
    This file is expected to be generated by the `extract_repository_details` tool.

    Args:
        path: Path to the JSON file containing the extracted repository details.
              Defaults to 'extract_repository_details.json'.
              If a directory is provided, will look for the JSON file in that directory.
        include_summary: If True, include the summary in the response.
        include_tree: If True, include the tree structure in the response.
        include_content: If True, include the file contents in the response.

    Returns:
        A dict with the loaded repository details containing the requested parts:
        - summary (str): Overview of the repository (if include_summary=True)
        - tree (str): Directory structure (if include_tree=True)
        - content (str): File contents (if include_content=True)
    """
    # If path is a directory, look for the default JSON file in that directory
    if os.path.isdir(path):
        path = os.path.join(path, GITINGEST_DEFAULT_OUTPUT_LOCATION)
    if not os.path.exists(path):
        return {"success": False, "error": f"File not found: {path}"}
    if not os.path.isfile(path):
        return {"success": False, "error": f"Path is not a file: {path}"}

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        result = {"success": True}

        if include_summary and "summary" in data:
            result["summary"] = data["summary"]

        if include_tree and "tree" in data:
            result["tree"] = data["tree"]

        if include_content and "content" in data:
            result["content"] = data["content"]

        return result

    except json.JSONDecodeError:
        return {"success": False, "error": "Invalid JSON format in file"}
    except Exception as e:
        return {"success": False, "error": f"Error loading file: {str(e)}"}
