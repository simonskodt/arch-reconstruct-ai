"""Tool Schema Validator Utility Function."""
from typing import Iterable
from langchain.tools import BaseTool

class ToolSchemaFixer:
    """Utility class for fixing tool schema issues."""

    @staticmethod
    def fix_empty_properties(tools: Iterable[BaseTool]) -> None:
        """
        Fix tools with incomplete args_schema by adding empty properties.

        This is a fix for tools fetched from MCP that may have incomplete schemas.

        Args:
            tools: An iterable of tool objects that may have an args_schema attribute.

        Returns:
            None: This function modifies the tools in-place.

        Note:
            Only modifies tools where args_schema is exactly equal to
            {"type": "object"}. Tools with other schema structures are left unchanged.
        """
        for tool in tools:
            if getattr(tool, "args_schema", None) == {"type": "object"}:
                tool.args_schema = {"type": "object", "properties": {}}
