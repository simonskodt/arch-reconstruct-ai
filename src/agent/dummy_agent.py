"""
This file defines a barebones agent.
"""
import os
import sys
import asyncio


from langchain.agents.middleware import HumanInTheLoopMiddleware
from langchain.agents import create_agent

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

MODEL = "openai:gpt-5-nano"
agent = create_agent(
    MODEL,
    tools=tools + [],
    system_prompt="Your are a helpful assistant.",
    middleware=[HumanInTheLoopMiddleware(interrupt_on=tool_interrupt_configuration),
                PersistentPlanningMiddleware()],
    state_schema=SoftwareAgentState
)
