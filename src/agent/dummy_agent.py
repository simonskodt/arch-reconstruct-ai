"""
This file defines a barebones agent.
"""
import asyncio
import os
import sys
from langchain.agents import create_agent


# NECESSARY: In order to enable imports from local modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
# pylint: disable=wrong-import-position
from src.agent.tools.github import git_clone_tool
from src.agent.tools.human_in_the_loop import add_human_in_the_loop, weather_tool
from src.mcp.mcp_client_factory import create_mcp_client_from_config


mcp_client = create_mcp_client_from_config()
mcp_tools = asyncio.run(mcp_client.get_tools())

tools = [git_clone_tool, weather_tool]
combine_tools = tools + mcp_tools


tools = [add_human_in_the_loop(t) for t in combine_tools]
agent = create_agent(
    "openai:gpt-4.1-nano",
    tools=tools,
    prompt="Your are a helpful assistant.",
)
