"""
This file defines a barebones agent.
"""
import os
import sys

from langchain.agents.middleware import LLMToolSelectorMiddleware
from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware #, InterruptOnConfig

# NECESSARY: In order to enable imports from local modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
# pylint: disable=wrong-import-position
from src.agent.tools.drawing import get_drawing_tools

from src.agent.tools.planning import PersistentPlanningMiddleware
from src.agent.tools.human_in_the_loop.config import DefaultInterruptConfig
from src.agent.tools.human_in_the_loop.human_in_the_loop import(
    create_human_in_the_loop_configuration,
    apply_interrupt_config_or_default
)

from src.agent.tools.navigation import get_navigation_tools, get_file_management_tools
from src.agent.tools.github import (
    git_clone_tool,
    extract_repository_details,
    load_extracted_repository
)

from src.agent.tools.archlens import (
    run_archLens,
    init_archLens,
    read_archLens_config_file,
    write_archLens_config_file,
    create_archLens_config_object,
    add_view_to_archLens_config_object
)

navigation_tools = get_navigation_tools()
file_management_tools = get_file_management_tools()
drawing_tools = get_drawing_tools()
tools = [git_clone_tool,
         extract_repository_details,
         load_extracted_repository, run_archLens, init_archLens,
         read_archLens_config_file, write_archLens_config_file,
         create_archLens_config_object, add_view_to_archLens_config_object]
+ drawing_tools + navigation_tools + file_management_tools


always_included_tools = [nav_tool.name for nav_tool in navigation_tools]
tool_selector = LLMToolSelectorMiddleware(
    model="openai:gpt-4.1-nano", # cheap model for tool selection
    max_tools=2,
    always_include=always_included_tools,
)
tools += navigation_tools + file_management_tools
apply_interrupt_config_or_default(tools, DefaultInterruptConfig)

tool_interrupt_configuration = create_human_in_the_loop_configuration(tools)

MODEL = "openai:gpt-5-nano"
agent = create_agent(
    MODEL,
    tools=tools,
    system_prompt="Your are a helpful assistant.",
    middleware=[HumanInTheLoopMiddleware(interrupt_on=tool_interrupt_configuration),
                PersistentPlanningMiddleware()]
)
