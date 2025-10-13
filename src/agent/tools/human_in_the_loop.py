"""A module to add human-in-the-loop review to tools."""
from typing import Callable
from langgraph.types import interrupt, Command
from langchain.agents.middleware.human_in_the_loop import HumanInTheLoopConfig
from langchain.agents.middleware.human_in_the_loop import HumanInTheLoopRequest
from langchain_core.tools import BaseTool
from langchain_core.messages import ToolMessage
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
        try:
            if response is None:
                return create_tool_message_and_command({
                    "type": "response",
                    "error": "No response from interrupt"
                }, config)
                # return "No response from interrupt"
            if str(response["type"]).lower() not in ["accept", "edit", "response"]:
                return create_tool_message_and_command({"type": "response","error":
                    f"Please make sure your response contains a key 'type' and a value for it \
                    (accept, edit, response). "
                    f"Response received: {response}"})
        # disable broad except pylint: disable=broad-exception-caught
        except Exception as e:

            return create_tool_message_and_command({
                "type": "response",
                "error": f"No response from interrupt: {e}"
            }, config)
            # return "No response from interrupt"
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
            return create_tool_message_and_command({
                "type": "response",
                "error": error_msg
            }, config)             # raise ValueError(error_msg)

        return tool_response

    return call_tool_with_interrupt


def create_tool_message_and_command(
    tool_response: dict,
    config: RunnableConfig | None = None
) -> Command:
    """
    Create a ToolMessage and Command from the tool response.
    to resume the interrupt with updated state.
    fixes issues with returning Command directly from tool. and interrupt not resuming properly.
    i.e. resetting state of response.
    """

    # Create a ToolMessage to pair with the tool call
    tool_call_id = config.toolCall.id if config and hasattr(config, "toolCall") else None
    if tool_call_id is None:
        # Handle missing tool call id if needed
        tool_call_id = "unknown_tool_call_id"

    tool_message = ToolMessage(content=tool_response, tool_call_id=tool_call_id)

    # Return a Command that resumes the interrupt and updates the state with the ToolMessage
    return Command(
        resume=tool_response,
        update={"messages": [tool_message]}
    )
