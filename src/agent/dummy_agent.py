"""
This file defines a barebones agent.
"""
import os
import sys
import asyncio

from langchain.agents import create_agent
from langchain.agents.middleware.summarization import SummarizationMiddleware
from langchain.agents.middleware import LLMToolSelectorMiddleware
from langchain_community.tools import BraveSearch


# NECESSARY: In order to enable imports from local modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
# pylint: disable=wrong-import-position
from src.agent.config import ARCHITECTURAL_RECONSTRUCTION_PROMPT
from src.agent.tools.planning import PersistentPlanningMiddleware

from src.utils.services import check_service_availability
from src.mcp.mcp_client_factory import create_mcp_client_from_config
from src.utils.validate_tools import ToolSchemaFixer

# tools
from src.agent.tools.drawing import get_drawing_tools
from src.agent.tools.navigation import get_navigation_tools, get_file_management_tools
from src.agent.tools.drawing.plantuml import PlantUMLDocumentationTool
from src.agent.tools.git.github import (
    git_clone_tool,
    extract_repository_details,
    load_extracted_repository
)

check_service_availability()
mcp_client = create_mcp_client_from_config()
# tools = archLens_mcp_tools + langChain_mcp_tools
brave_search = BraveSearch().from_search_kwargs({"max_results": 5})
context7_tools = asyncio.run(mcp_client.get_tools(server_name="context7"))
ToolSchemaFixer.fix_empty_properties(context7_tools) # Fix tools with empty properties (MCP issue)

# Create PlantUML documentation tool instance
plantuml_tool = PlantUMLDocumentationTool(context7_tools)


tools = get_drawing_tools() + \
    get_navigation_tools() + \
    get_file_management_tools() + \
    plantuml_tool.get_tools() + \
    [git_clone_tool, extract_repository_details, load_extracted_repository, brave_search]


# Agent Middleware
MODEL = "openai:gpt-{number}-nano"
summarization_tool = SummarizationMiddleware(MODEL.format(number="4.1"),
                                             max_tokens_before_summary=10_000,
                                             messages_to_keep=5)


always_included_tools = []
tool_selector = LLMToolSelectorMiddleware(
    model=MODEL.format(number="4.1"),
    system_prompt= \
    "You are a tool selection middleware for an architectural reconstruction agent. \n" \
    "Your task is to select the most relevant tools for answering user queries related \
    to software architecture reconstruction, " \
    "including module, component-and-connector, and deployment diagrams, " \
    "as well as PlantUML syntax and examples.",
    max_tools=3,
    always_include=always_included_tools,
)

agent = create_agent(
    MODEL.format(number="5"),
    tools=tools,
    system_prompt=ARCHITECTURAL_RECONSTRUCTION_PROMPT,
    middleware=[PersistentPlanningMiddleware(), summarization_tool, tool_selector],
)
