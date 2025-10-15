"""
This file defines a barebones agent.
"""
import os
import sys
from langchain.agents import create_agent


# NECESSARY: In order to enable imports from local modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
# pylint: disable=wrong-import-position
from src.agent.tools.github import (
    git_clone_tool,
    extract_repository_details,
    load_extracted_repository
)


tools = [git_clone_tool, extract_repository_details, load_extracted_repository]

MODEL = "openai:gpt-4.1-nano"
agent = create_agent(
    MODEL,
    tools=tools,
    prompt="You are a helpful assistant.",
)
