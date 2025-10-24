"""
Agent State Management Module

This module provides classes and utilities for managing agent state,
particularly for tracking repositories, diagrams, and other resources.
"""
from typing import Annotated
from src.agent.tools.planning import PersistentPlanningState

def merge_dicts(left: dict, right: dict) -> dict:
    """
    Merge two dictionaries with nested structure support.

    Args:
        left: Base dictionary
        right: Dictionary to merge in

    Returns:
        Merged dictionary where nested dicts are merged recursively
    """
    result = left.copy()

    for key, value in right.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            # Both are dicts, merge recursively
            result[key] = merge_dicts(result[key], value)
        else:
            # Not both dicts, or key doesn't exist in left, overwrite
            result[key] = value

    return result

class SoftwareAgentState(PersistentPlanningState):
    """Custom persistent planning state to store additional info if needed."""
    repositories: Annotated[dict, merge_dicts]  # To track cloned repositories with analysis data
    diagrams: Annotated[dict, merge_dicts]  # To track created diagrams with metadata
