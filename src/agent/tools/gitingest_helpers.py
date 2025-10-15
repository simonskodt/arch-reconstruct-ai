"""
Helper functions for gitingest operations to avoid blocking async event loops.
"""
import asyncio
import os
from typing import Optional

from gitingest.ingestion import ingest_query
from gitingest.query_parser import parse_local_dir_path
from gitingest.utils.ignore_patterns import load_ignore_patterns
from gitingest.utils.pattern_utils import process_patterns
from gitingest.config import MAX_FILE_SIZE


async def ingest_local_non_blocking(
    source: str,
    *,
    max_file_size: int = MAX_FILE_SIZE,
    exclude_patterns: Optional[set[str]] = None,
    include_patterns: Optional[set[str]] = None,
    include_gitignored: bool = False,
) -> tuple[str, str, str]:
    """
    Non-blocking wrapper around gitingest that avoids Path.resolve() blocking.

    This function manually calls parse_local_dir_path in a thread to avoid
    blocking the event loop with Path.resolve().

    Args:
        source: Local directory path to ingest.
        max_file_size: Maximum file size to process.
        exclude_patterns: Set of patterns to exclude.
        include_patterns: Set of patterns to include.
        include_gitignored: Whether to include gitignored files.

    Returns:
        Tuple of (summary, tree, content) strings.
    """
    # Parse the local directory path in a thread to avoid blocking
    query = await asyncio.to_thread(parse_local_dir_path, source)

    query.max_file_size = max_file_size
    query.ignore_patterns, query.include_patterns = process_patterns(
        exclude_patterns=exclude_patterns,
        include_patterns=include_patterns,
    )

    if not include_gitignored:
        # Load gitignore patterns (also needs to run in thread as it does file I/O)
        for fname in (".gitignore", ".gitingestignore"):
            ignore_pats = await asyncio.to_thread(
                load_ignore_patterns,
                query.local_path,
                filename=fname
            )
            query.ignore_patterns.update(ignore_pats)

    # ingest_query is CPU-bound but doesn't do blocking I/O
    summary, tree, content = await asyncio.to_thread(ingest_query, query)

    return summary, tree, content

def normalize_path(local_repository_path: str, cwd: str) -> str:
    r"""
    Normalize the repository path to an absolute path.

    Handles paths starting with \ or / that are relative to drive root,
    and converts relative paths to absolute using cwd.
    """
    # Handle paths that start with \ or / (relative to drive root, not truly absolute)
    if local_repository_path.startswith(('\\', '/')) and not (
        len(local_repository_path) > 1 and local_repository_path[1] == ':'
    ):
        local_repository_path = local_repository_path.lstrip('\\/')

    # Convert to absolute path
    if not os.path.isabs(local_repository_path):
        path = os.path.join(cwd, local_repository_path)
    else:
        path = local_repository_path
    return path
