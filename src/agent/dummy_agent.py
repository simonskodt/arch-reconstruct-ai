"""
This file defines a barebones agent.
"""
import os
import sys
import asyncio

from langchain.agents import create_agent
from langchain.agents.middleware.summarization import SummarizationMiddleware
from langchain.agents.middleware import LLMToolSelectorMiddleware


# NECESSARY: In order to enable imports from local modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
# pylint: disable=wrong-import-position
from src.utils.services import check_service_availability
from src.agent.tools.planning import PersistentPlanningMiddleware

# tools
from src.mcp.mcp_client_factory import create_mcp_client_from_config
from src.utils.validate_tools import ToolSchemaFixer

from src.agent.tools.drawing import get_drawing_tools
from src.agent.tools.navigation import get_navigation_tools, get_file_management_tools
from src.agent.tools.github import (
    git_clone_tool,
    extract_repository_details,
    load_extracted_repository
)

check_service_availability()
mcp_client = create_mcp_client_from_config()
# tools = archLens_mcp_tools + langChain_mcp_tools
brave_search = asyncio.run(mcp_client.get_tools(server_name="brave-search"))
context7_tools = asyncio.run(mcp_client.get_tools(server_name="context7"))
ToolSchemaFixer.fix_empty_properties(brave_search) # Fix tools with empty properties (MCP issue)

tools = [
    git_clone_tool,
    extract_repository_details,
    load_extracted_repository,
] + get_drawing_tools()


MODEL = "openai:gpt-{number}-nano"
summarization_tool = SummarizationMiddleware(MODEL.format(number="4.1"),
                                             max_tokens_before_summary=5000,
                                             messages_to_keep=5)

navigation_tools = get_navigation_tools()
file_management_tools = get_file_management_tools()

always_included_tools = [nav_tool.name for nav_tool in navigation_tools]
tool_selector = LLMToolSelectorMiddleware(
    model="openai:gpt-4.1-nano", # cheap model for tool selection
    max_tools=2,
    always_include=always_included_tools,
)

agent = create_agent(
    MODEL.format(number="5"),
    tools=tools,
    system_prompt="You are a helpful assistant.",
    middleware=[summarization_tool, PersistentPlanningMiddleware(), tool_selector],
)
