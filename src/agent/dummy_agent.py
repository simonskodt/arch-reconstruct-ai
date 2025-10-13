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
from src.mcp.mcp_client_factory import create_mcp_client_from_config
from src.agent.tools.planning import AsyncPlanningMiddleware
from src.utils.validate_tools import ToolSchemaFixer

mcp_client = create_mcp_client_from_config()
archLens_mcp_tools = asyncio.run(mcp_client.get_tools(server_name="ArchLensGitRepoMCP"))
langChain_mcp_tools = asyncio.run(mcp_client.get_tools(server_name="LangChainGitRepoMCP"))


tools = archLens_mcp_tools + langChain_mcp_tools
ToolSchemaFixer.fix_empty_properties(tools) # Fix tools with empty properties (MCP issue)
MODEL = "openai:gpt-4.1-nano"
agent = create_agent(
    MODEL,
    tools=tools,
    system_prompt="You are a helpful assistant.",
    middleware=[AsyncPlanningMiddleware()]
)
