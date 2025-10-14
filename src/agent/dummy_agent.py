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
from src.utils.validate_tools import ToolSchemaFixer
from src.agent.tools.navigation import get_navigation_tools

mcp_client = create_mcp_client_from_config()
mcp_tools = asyncio.run(mcp_client.get_tools())
ToolSchemaFixer.fix_empty_properties(mcp_tools) # Fix tools with empty properties (MCP issue)
navigation_tools = get_navigation_tools()
tools = mcp_tools + navigation_tools
MODEL = "openai:gpt-5-nano"
agent = create_agent(
    MODEL,
    tools=tools,
    system_prompt="You are a helpful assistant.",
)
