"""Human-in-the-loop (HITL) helper utilities.

This module provides a method for creating a human-in-the-loop configuration
and a decorator, `tool_with_interrupt_config`, that
attaches an interrupt configuration to a function or tool object without
wrapping it.

Usage notes:
there are two main ways to use this decorator:
- Apply the `@tool_with_interrupt_config(...)` annotation to the raw function before the
  `@tool(...)` decorator from langchain (i.e. put `@tool` above
  `@tool_with_interrupt_config` in source)
- Use `apply_interrupt_config_or_default(tool, config)` to programmatically attach a
  config to an existing tool object.
- either way, create_human_in_the_loop_configuration(tools) below will find the configuration.

Example:

    from langchain_core.tools import tool

    @tool("weather_tool")
    @tool_with_interrupt_config(InterruptOnConfig(
        allowed_decisions=["approve", "edit"],
        description="Get weather information."
        )
    )
    def weather_tool(location: str) -> str:
        return f"The weather in {location} is sunny."


    # Or on a existing tool object:
    tool_1 = tool(some_function)
    apply_interrupt_config_or_default(tool_1,
        InterruptOnConfig(
            allowed_decisions=["approve", "reject"],
            description="DEFAULT_INTERRUPT_DESCRIPTION",
        )
    )
    # tool_interrupt_configuration = create_human_in_the_loop_configuration([tool_1, tool_2,...,])
    # will discover the attached config and include it to be used for human-in-the-loop middleware.
"""
import inspect
from typing import Any, Callable, Dict, Iterable
from langchain.agents.middleware.human_in_the_loop import InterruptOnConfig
from langchain_core.tools import BaseTool

from .config import (
    DefaultInterruptConfig, DEFAULT_INTERRUPT_DESCRIPTION
)


def tool_with_interrupt_config(
        interrupt_config: InterruptOnConfig
    ) -> Callable[[Callable], Callable]:
    """Decorator that attaches `_interrupt_config` metadata to a function.

    This decorator intentionally does NOT wrap the target callable. It simply
    sets an attribute on the function (or object) so the metadata can be
    discovered later by `create_human_in_the_loop_configuration`.
    """
    def decorator(fn: Callable) -> Callable:
        setattr(fn, "_interrupt_config", interrupt_config)
        return fn

    return decorator

def create_human_in_the_loop_configuration(
        tools: Iterable[BaseTool]
    ) -> Dict[str, bool | InterruptOnConfig]:
    """Build an interrupt configuration map from a list of tools.

    The returned dict maps tool names (tool.name) to either an
    InterruptOnConfig-like instance/dict (if the tool was annotated) or False
    (no interrupt requested for that tool).
    """

    result: Dict[str, bool | InterruptOnConfig] = {}
    for tool_obj in tools:
        tool_name = getattr(tool_obj, "name", None) or \
            getattr(tool_obj, "__name__", None) or \
            tool_obj.__class__.__name__
        cfg = _discover_tool_interrupt_config(tool_obj)
        if cfg is not None:
            result[tool_name] = cfg
        else:
            result[tool_name] = False

    return result

def _discover_tool_interrupt_config(tool_obj: Any) -> Any:
    """Find an attached InterruptOnConfig on a tool or callable.

    The discovery process tries common locations where the metadata
    may live:
    - attribute `_interrupt_config` on the tool object itself
    - attribute `_interrupt_config` on a wrapped function (`.func`),
      callable, or on the function underlying a callable (via __wrapped__ chain)

    Returns the config (InterruptOnConfig or dict) if found, otherwise None.
    """
    cfg = getattr(tool_obj, "_interrupt_config", None)
    if cfg is not None:
        return cfg

    # Some tool wrappers store the underlying function on `.func`
    underlying = getattr(tool_obj, "func", None)
    if underlying is None and callable(tool_obj):
        # For objects that implement __call__, inspect the bound method
        underlying = getattr(tool_obj, "__call__", None)

    if underlying:
        try:
            original = inspect.unwrap(underlying)
        except (AttributeError, TypeError):
            original = underlying
        cfg = getattr(original, "_interrupt_config", None)
        if cfg is not None:
            return cfg
    return None

def apply_interrupt_config_or_default(
        tools: BaseTool | Iterable[BaseTool],
        config: bool | InterruptOnConfig | None,
        overwrite: bool = False
    ):
    """Apply a interrupt configuration or default to a list of tools."""
    if config is None:
        config = DefaultInterruptConfig
    elif isinstance(config, bool) and config:
        config = InterruptOnConfig(
            allowed_decisions=["approve", "edit", "reject"],
            description=DEFAULT_INTERRUPT_DESCRIPTION
        )
    for tool_obj in tools:
        if config is not False:
            _attach_interrupt_config(tool_obj, config, overwrite)
    return tools

def _attach_interrupt_config(
        tool_obj: Any,
        interrupt_config: InterruptOnConfig,
        overwrite: bool = False
    ) -> Any:
    """Attach an interrupt configuration to a tool object (if not already present).
    This is a utility function to set the `_interrupt_config` attribute
    on a tool object.

    Args:
        tool: The tool object (function, BaseTool instance, etc.)
        interrupt_config: The InterruptOnConfig to attach

    Returns:
        The tool object with the interrupt_config attached.
    """
    if _discover_tool_interrupt_config(tool_obj) is None or overwrite:
        tool_with_interrupt_config(interrupt_config)(tool_obj)
    return tool_obj
