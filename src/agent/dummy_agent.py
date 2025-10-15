"""
This file defines a barebones agent.
"""
import os
import sys

from langchain.agents import create_agent
from langchain.agents.middleware import LLMToolSelectorMiddleware

# NECESSARY: In order to enable imports from local modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
# pylint: disable=wrong-import-position
from src.agent.tools.navigation import get_navigation_tools, get_file_management_tools
from src.agent.tools.github import git_clone_tool


navigation_tools = get_navigation_tools()
file_management_tools = get_file_management_tools()

always_included_tools = [nav_tool.name for nav_tool in navigation_tools]
tool_selector = LLMToolSelectorMiddleware(
    model="openai:gpt-4.1-nano", # cheap model for tool selection
    max_tools=2,
    always_include=always_included_tools,
)

tools = navigation_tools + file_management_tools + [git_clone_tool]
MODEL = "openai:gpt-5-nano"
agent = create_agent(
    MODEL,
    tools=tools,
    system_prompt="You are a helpful assistant.",
    middleware=[tool_selector]
)
