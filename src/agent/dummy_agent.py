"""
This file defines a barebones agent.
"""
import asyncio
import os
import sys
from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware #, InterruptOnConfig

# NECESSARY: In order to enable imports from local modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
# pylint: disable=wrong-import-position
from src.mcp.mcp_client_factory import create_mcp_client_from_config
from .tools.github import git_clone_tool
from .tools.human_in_the_loop.config import DEFAULT_INTERRUPT_CONFIG
from .tools.human_in_the_loop.human_in_the_loop import(
    create_human_in_the_loop_configuration,
    apply_interrupt_config_or_default
)

mcp_client = create_mcp_client_from_config()
mcp_tools = asyncio.run(mcp_client.get_tools())

tools = [git_clone_tool]
combined_tools = tools + mcp_tools

apply_interrupt_config_or_default(mcp_tools, True)
apply_interrupt_config_or_default(tools, DEFAULT_INTERRUPT_CONFIG)

tool_interrupt_configuration = create_human_in_the_loop_configuration(combined_tools)
agent = create_agent(
    "openai:gpt-4.1-nano",
    tools=combined_tools,
    system_prompt="Your are a helpful assistant.",
    middleware=[HumanInTheLoopMiddleware(interrupt_on=tool_interrupt_configuration)]
)
