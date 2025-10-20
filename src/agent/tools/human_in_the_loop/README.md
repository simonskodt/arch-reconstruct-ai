# Module: `src.agent.tools.human_in_the_loop`

> [!NOTE]
> The interface for responding to interrupts is delicate and needs more validation. See [human_in_the_loop_response_examples.md](human_in_the_loop_response_examples.md) for detailed information, response guide with **examples**, and tips on improving the user experience.

## Quick Usage

- Import the decorator and configuration functions from the module.
- Annotate tool functions with `@tool_with_interrupt_config` before applying `@tool`, or use `apply_interrupt_config_or_default` on existing tool objects.
- Call `create_human_in_the_loop_configuration(tools)` to generate the interrupt config map for use with `HumanInTheLoopMiddleware`.

Example setup in an agent:

```python
from src.agent.tools.human_in_the_loop import (
    tool_with_interrupt_config,
    create_human_in_the_loop_configuration,
    apply_interrupt_config_or_default,
)
from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langchain.agents.middleware.human_in_the_loop import InterruptOnConfig

# Annotate a tool
@tool("my_tool")
@tool_with_interrupt_config(InterruptOnConfig(
    allowed_decisions=["approve", "edit", "reject"],
    description="Review this tool call."
))
def my_tool(param: str) -> str:
    return f"Processed {param}"

# Or apply to existing tools
tools = [my_tool, other_tool]
apply_interrupt_config_or_default(tools, True)  # Apply default config

# Build config for middleware
interrupt_config = create_human_in_the_loop_configuration(tools)

# Use in agent
agent = create_agent(
    "openai:gpt-4",
    tools=tools,
    middleware=[HumanInTheLoopMiddleware(interrupt_on=interrupt_config)]
)
```
