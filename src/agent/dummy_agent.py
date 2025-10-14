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
from src.agent.tools.planning import PersistentPlanningMiddleware
from src.utils.validate_tools import ToolSchemaFixer

mcp_client = create_mcp_client_from_config()
# tools = archLens_mcp_tools + langChain_mcp_tools
brave_search = asyncio.run(mcp_client.get_tools(server_name="brave-search"))
ToolSchemaFixer.fix_empty_properties(brave_search) # Fix tools with empty properties (MCP issue)



MODEL = "openai:gpt-4.1-nano"
agent = create_agent(
    MODEL,
    tools=brave_search,
    system_prompt="You are a helpful assistant.",
    middleware=[PersistentPlanningMiddleware()]
)
