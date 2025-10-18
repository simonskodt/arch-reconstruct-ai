"""
This file defines a barebones agent.
"""
import asyncio
import os
import sys
from langchain.agents import create_agent
from langchain.agents.middleware.summarization import SummarizationMiddleware

# NECESSARY: In order to enable imports from local modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
# pylint: disable=wrong-import-position
from src.utils.services import check_service_availability
from src.mcp.mcp_client_factory import create_mcp_client_from_config
from src.agent.tools.planning import PersistentPlanningMiddleware
from src.utils.validate_tools import ToolSchemaFixer

# tools
from src.agent.tools.drawing import get_drawing_tools
from src.agent.tools.github import (
    git_clone_tool,
    extract_repository_details,
    load_extracted_repository
)

check_service_availability()
mcp_client = create_mcp_client_from_config()
# tools = archLens_mcp_tools + langChain_mcp_tools
brave_search = asyncio.run(mcp_client.get_tools(server_name="brave-search"))
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

agent = create_agent(
    MODEL.format(number="5"),
    tools=tools,
    system_prompt="You are a helpful assistant.",
    middleware=[summarization_tool, PersistentPlanningMiddleware()],
)
