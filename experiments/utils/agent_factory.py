"""
Agent factory provides utilities to create agents with properly validated tools,
ensuring that tool schemas are correctly formatted before agent creation.
"""

from langchain.agents import create_agent

def ensure_tools_have_valid_schema(tools):
    """
    This function validates and corrects the args_schema attribute of tools.
    If a tool's args_schema is exactly {"type": "object"}, it updates it to
    {"type": "object", "properties": {}} to ensure proper schema structure.

    Args:
        tools (list): A list of tool objects that may have an args_schema attribute.

    Returns:
        None: This function modifies the tools in-place.

    Note:
        The function only modifies tools where args_schema is exactly equal to
        {"type": "object"}. Tools with other schema structures are left unchanged.
    """
    for tool in tools:
        if getattr(tool, "args_schema", None) == {"type": "object"}:
            tool.args_schema = {"type": "object", "properties": {}}

def create_agent_with_valid_tools(*args, tools=None, **kwargs):
    """
    Create an agent with validated tools.
    This function wraps the create_agent function to ensure that any provided tools
    have valid schemas before creating the agent. It validates the tools using
    ensure_tools_have_valid_schema and then passes all arguments to create_agent.

    Args:
        *args: Variable length argument list to pass to create_agent.
        tools (list, optional): List of tools to validate and include with the agent.
            If None, no tools validation is performed. Defaults to None.
        **kwargs: Arbitrary keyword arguments to pass to create_agent.

    Returns:
        The result of create_agent with validated tools (if provided).

    Raises:
        Any exceptions raised by ensure_tools_have_valid_schema during tool validation
        or by create_agent during agent creation.
    """

    if tools is not None:
        ensure_tools_have_valid_schema(tools)
        kwargs["tools"] = tools
    return create_agent(*args, **kwargs)
