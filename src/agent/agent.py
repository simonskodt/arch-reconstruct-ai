"""
Orchestrates the two-stage software reconstruction agent pipeline.
"""

import os
import sys
from typing import Annotated, Any

from langchain.agents.middleware import HumanInTheLoopMiddleware, after_model
from langchain.agents import create_agent
from langchain.messages import RemoveMessage
from langchain.tools.tool_node import ToolMessage
from langchain_core.tools import InjectedToolCallId
from langgraph.graph import StateGraph, START, END
from langgraph.types import Command
from langgraph.runtime import Runtime

# NECESSARY: In order to enable imports from local modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
# pylint: disable=wrong-import-position
from src.agent.tools.drawing import get_drawing_tools

from src.agent.tools.navigation.util import get_workspace_root
from src.agent.tools.planning import PersistentPlanningMiddleware, PersistentPlanningState
from src.agent.tools.human_in_the_loop.config import DefaultInterruptConfig
from src.agent.tools.human_in_the_loop.human_in_the_loop import (
    create_human_in_the_loop_configuration,
    apply_interrupt_config_or_default,
)

from src.agent.tools.navigation import (
    get_navigation_tools,
    get_file_management_tools,
    change_directory,
    navigate_to_repository,
)
from src.agent.tools.github import (
    git_clone_tool,
    extract_repository_details,
    load_extracted_repository,
)

navigation_tools = get_navigation_tools()
file_management_tools = get_file_management_tools()
drawing_tools = get_drawing_tools()
tools = (
    [load_extracted_repository]
    + drawing_tools
    + file_management_tools
)

apply_interrupt_config_or_default(tools, DefaultInterruptConfig)

tool_interrupt_configuration = create_human_in_the_loop_configuration(tools)

MODEL = "openai:gpt-5-nano"

class SoftwareAgentState(PersistentPlanningState):
    """State to extract repos."""
    has_extracted_repo: Annotated[bool, "boolean that checks if the repository has been extracted"]

async def prepare_workspace(
    state: SoftwareAgentState,
    repo_url: str,
    tool_call_id: Annotated[str, InjectedToolCallId],
    workspace: str = str(get_workspace_root())
) -> str:
    """
    Prepare the local workspace for working with a git repository.

    Args:
        repo_url : str
            URL of the git repository to clone.
        workspace : str, optional
            Filesystem path to use as the workspace directory.

    Returns:
        str
            Outcome of setting up model.
    """
    print(f"workspace type: {type(workspace)}, value: {workspace}")
    repo_name = repo_url.split("/")[-1]

    change_directory.invoke({"path": workspace})
    git_clone_tool.invoke({"repo_url": repo_url, "dest": repo_name})
    navigate_to_repository.invoke({"repo_name": repo_name})
    await extract_repository_details.ainvoke(
        {"local_repository_path": f"agent_workspace/repositories/{repo_name}"})

    state['has_extracted_repo'] = True
    return Command(update={
                "messages": [ToolMessage(
                    content="Successfully cloned and extracted repo", tool_call_id=tool_call_id)],
                "has_extracted_repo": True
            }
        )

@after_model
def clear_message(state: SoftwareAgentState, _: Runtime) -> dict[str, Any] | None:
    """Method for cleaning messages before passing to other agent."""
    messages = state["messages"]
    if messages and messages[-1].type == "tool":
        return {"messages": [RemoveMessage(id=m.id) for m in messages[:1]]}
    return None

git_clone_agent = create_agent(
    MODEL,
    tools=[prepare_workspace],
    system_prompt=f"""
You are a repository extractor that clones a user-defined repository into a folder,
navigates to that folder, and then extracts the directory tree structure and all repository files into a single readable file.
This is done using the tool {prepare_workspace.__name__},
which you should call when the user provides a GitHub URL.

Please follow these rules:
- Never produce two AI messages in a row.
- After each AI message, wait for a human response.
""",
    middleware=[clear_message],
    state_schema=SoftwareAgentState
)

arch_recon_agent = create_agent(
    MODEL,
    tools=tools,
    system_prompt=f"""
You are an AI software architecture assistant specializing in repository/architectural reconstruction and documentation.
You have access to a repository and should help the user understand it.

You are currently at the root of a GitHub repository called kitty.
The repository's tree structure has been extracted,
and all files have been compiled into a single content file for easy reading.
Access these using the tool {load_extracted_repository.name}.

You can also help the user understand the repository tree structure by displaying the directory tree.
If the user asks about specific subfolders or files,
use {load_extracted_repository.name} to retrieve the directory tree and content from those files.

Present the user with your plan based on this system prompt and wait for their confirmation.
""",
    middleware=[HumanInTheLoopMiddleware(interrupt_on=tool_interrupt_configuration),
                PersistentPlanningMiddleware()]
)

graph_builder = StateGraph(SoftwareAgentState)
graph_builder.add_node("git_clone_agent", git_clone_agent)
graph_builder.add_node("arch_recon_agent", arch_recon_agent)

graph_builder.add_edge(START, "git_clone_agent")

graph_builder.add_conditional_edges(
    "git_clone_agent",
    lambda state: "arch_recon_agent" if state.get("has_extracted_repo")
        else "git_clone_agent",
    {
        "arch_recon_agent": "arch_recon_agent",
        "git_clone_agent": "git_clone_agent"
    }
)
graph_builder.add_edge("arch_recon_agent", END)

agent = graph_builder.compile()
