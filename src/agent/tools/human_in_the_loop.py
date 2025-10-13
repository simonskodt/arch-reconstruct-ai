"""A module to add human-in-the-loop review to tools."""
from typing import Callable
from langgraph.types import interrupt, Command
from langchain.agents.middleware.human_in_the_loop import HumanInTheLoopConfig
from langchain.agents.middleware.human_in_the_loop import HumanInTheLoopRequest
from langchain_core.tools import BaseTool
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool as create_tool


@create_tool("weather_tool")
def weather_tool(location: str) -> str:
    """Get weather information."""
    return f"The weather in {location} is sunny."

def add_human_in_the_loop(
    tool: Callable | BaseTool,
    *,
    interrupt_config: HumanInTheLoopConfig | None = None,
) -> BaseTool:
    """Wrap a tool to support human-in-the-loop review."""
    if not isinstance(tool, BaseTool):
        tool = create_tool(tool)

    if interrupt_config is None:
        interrupt_config = {
            "allow_accept": True,
            "allow_edit": True,
            "allow_respond": True,
        }

    @create_tool(
        tool.name,
        description=tool.description,
        args_schema=tool.args_schema
    )
    async def call_tool_with_interrupt(config: RunnableConfig, **tool_input):
        request: HumanInTheLoopRequest = {
            "action_request": {
                "action": tool.name,
                "args": tool_input
            },
            "config": interrupt_config,
            "description": "Please review the tool call below \
            and approve, edit, or provide feedback.\n"
            f"args_schema: {tool.args_schema}\n"
        }

        response = interrupt([request])

        # approve the tool call
        if str(response["type"]).lower() == "accept":
            tool_response = await tool.ainvoke(tool_input, config)

        # update tool call args
        elif str(response["type"]).lower() == "edit":
            tool_input = response["args"]["args"]
            tool_response = tool.ainvoke(tool_input, config)

        # respond to the LLM with user feedback
        elif str(response["type"]).lower() == "response":
            user_feedback = response["args"]
            tool_response = user_feedback
        else:
            error_msg = f"Unsupported interrupt response type: {response['type']}"
            response = None
            return Command(resume={"type": "response","error": error_msg})
            # return (f"Unsupported interrupt response type: {error_msg}")

        return tool_response

    return call_tool_with_interrupt
