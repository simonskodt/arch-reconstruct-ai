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
from src.agent.tools.planning import PersistentPlanningMiddleware
from src.utils.validate_tools import ToolSchemaFixer
from src.agent.tools.human_in_the_loop.config import DEFAULT_INTERRUPT_CONFIG
from src.agent.tools.human_in_the_loop.human_in_the_loop import(
    create_human_in_the_loop_configuration,
    apply_interrupt_config_or_default
)
from src.agent.tools.github import git_clone_tool

mcp_client = create_mcp_client_from_config()
brave_search = asyncio.run(mcp_client.get_tools(server_name="brave-search"))
ToolSchemaFixer.fix_empty_properties(brave_search) # Fix tools with empty properties (MCP issue)


tools = [git_clone_tool]
combined_tools = tools + brave_search

apply_interrupt_config_or_default(brave_search, True)
apply_interrupt_config_or_default(tools, DEFAULT_INTERRUPT_CONFIG)

tool_interrupt_configuration = create_human_in_the_loop_configuration(combined_tools)
agent = create_agent(
    "openai:gpt-4.1-nano",
    tools=combined_tools,
    system_prompt="Your are a helpful assistant.",
    middleware=[HumanInTheLoopMiddleware(interrupt_on=tool_interrupt_configuration),
                PersistentPlanningMiddleware()]
)
