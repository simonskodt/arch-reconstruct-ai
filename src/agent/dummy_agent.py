"""
This file defines a barebones agent.
"""
import os
import sys
import asyncio
from typing import Annotated


from langchain.agents.middleware import HumanInTheLoopMiddleware
from langchain.agents import create_agent
from langchain_core.messages import ToolMessage
from langchain_core.tools import tool, InjectedToolCallId
from langgraph.types import Command

# NECESSARY: In order to enable imports from local modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
# pylint: disable=wrong-import-position
from src.agent.software_agent_state import SoftwareAgentState
from src.agent.tools.planning import PersistentPlanningMiddleware
from src.agent.tools.human_in_the_loop.config import DefaultInterruptConfig
from src.agent.tools.human_in_the_loop.human_in_the_loop import(
    create_human_in_the_loop_configuration,
    apply_interrupt_config_or_default
)
from src.agent.tools.drawing import get_drawing_tools
from src.agent.tools.navigation import get_navigation_tools, get_file_management_tools
from src.agent.tools.github import (
    git_clone_tool,
    extract_repository_details,
    load_extracted_repository
)

# On Windows the default event loop may not support subprocesses.
# Ensure we use the ProactorEventLoop which implements subprocess APIs.
if sys.platform == "win32":
    try:
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    # pylint: disable=broad-exception-caught
    except Exception:
        # If not available for some Python build, continue and let errors surface
        pass

navigation_tools = get_navigation_tools()
file_management_tools = get_file_management_tools()
drawing_tools = get_drawing_tools()
tools = [git_clone_tool,
         extract_repository_details,
         load_extracted_repository] + drawing_tools + navigation_tools + file_management_tools


apply_interrupt_config_or_default(tools, DefaultInterruptConfig)

tool_interrupt_configuration = create_human_in_the_loop_configuration(tools)


@tool("update_state")
def update_state(input_text: str, tool_call_id: Annotated[str, InjectedToolCallId]) -> Command:
    """Update the state of the agent."""
    return Command(update={
        "messages": [ToolMessage(content=f"Updated state with: {input_text}",
                                 tool_call_id=tool_call_id)],
        "repositories": {
            str(input_text): {
                "path": str(input_text),
                "url": input_text,
            }
        }
    })

@tool("load_state")
def load_state(input_text: str, tool_call_id: Annotated[str, InjectedToolCallId]) -> Command:
    """load the state of the agent."""
    return Command(update={
        "messages": [ToolMessage(content=f"Loaded state with: {input_text}",
                                 tool_call_id=tool_call_id)],
        "repositories": {
            str(input_text): {
                "path": str(input_text),
                "url": input_text,
            }
        }
    })

@tool("load_tool_state")
def load_tool_state(input_text: str, tool_call_id: Annotated[str, InjectedToolCallId]):
    """load the state of the agent."""
    return Command(update={
        "messages": [ToolMessage(content=f"Updated state with: {input_text}",
                                 tool_call_id=tool_call_id)],
        "repositories": {
            str(input_text): {
                "path": str(input_text),
                "url": input_text,
            }
        }
    })


MODEL = "openai:gpt-5-nano"
agent = create_agent(
    MODEL,
    tools=[load_tool_state, update_state, git_clone_tool],
    system_prompt="Your are a helpful assistant.",
    middleware=[HumanInTheLoopMiddleware(interrupt_on=tool_interrupt_configuration),
                PersistentPlanningMiddleware()],
    state_schema=SoftwareAgentState
)
