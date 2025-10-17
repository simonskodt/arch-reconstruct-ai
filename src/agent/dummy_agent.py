"""
This file defines a barebones agent.
"""
import os
import sys
from langchain.agents import create_agent


# NECESSARY: In order to enable imports from local modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
# pylint: disable=wrong-import-position
# from src.utils.services import check_service_availability

# tools
from src.retrieval.builder import diag_tool
from src.agent.tools.drawing import get_drawing_tools
from src.agent.tools.github import (
    git_clone_tool,
    extract_repository_details,
    load_extracted_repository
)

# check_service_availability()

tools = [
    git_clone_tool,
    extract_repository_details,
    load_extracted_repository,
    diag_tool
] + get_drawing_tools()

MODEL = "openai:gpt-4.1-nano"
agent = create_agent(
    MODEL,
    tools=tools,
    system_prompt="You are a helpful assistant.",
)
