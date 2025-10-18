"""
PlantUML documentation retrieval tool using Context7 MCP server.
"""
import json
import os
from datetime import datetime
from typing import Optional
from langchain.tools import tool, BaseTool


class PlantUMLDocumentationTool:
    """
    A tool class for retrieving PlantUML documentation using the Context7 MCP server.

    This class targets the PlantUML library specifically, ensuring all searches
    return documentation only from PlantUML sources.
    """

    def __init__(self, tools: list[BaseTool], log_file: str = "plantuml_queries.log"):
        """
        Initialize the PlantUML documentation tool.

        Args:
            tools: List of tools obtained from the MCP client Upstash.
            log_file: Path to the file where queries and results will be logged
        """
        self.tools = tools
        self.plantuml_library_id = "/plantuml/plantuml"
        self.upstash_doc_tool_name = 'get-library-docs'
        self.upstash_plantuml_tool = next((tool for tool in self.tools if hasattr(tool, 'name') \
                                           and self.upstash_doc_tool_name in tool.name), None)
        self.log_file = log_file

    def plantuml_documentation_search(
        self,
        query: str,
        tokens: Optional[int] = 5000
    ) -> str:
        """
        Search PlantUML documentation and syntax reference.

        This tool searches the official PlantUML documentation to provide
        accurate syntax, examples, and usage information for creating diagrams.

        Args:
            query: The search query for PlantUML documentation (e.g.,
                "class diagram syntax",
                "sequence diagram")
            tokens: Maximum number of tokens to retrieve (default: 5000)

        Returns:
            Relevant PlantUML documentation and examples matching the query.
        """
        return self._search_plantuml_docs(query, tokens or 5000)

    def plantuml_syntax_lookup(
        self,
        diagram_type: str,
        specific_feature: Optional[str] = None
    ) -> str:
        """
        Get specific PlantUML syntax for diagram types and features.

        Args:
            diagram_type: Type of diagram (e.g.,
                "class", "sequence",
                "usecase", "activity",
                "component")
            specific_feature: Optional specific feature to look up (e.g.,
                "relationships",
                "stereotypes",
                "notes")

        Returns:
            PlantUML syntax reference for the specified diagram type and feature.
        """
        query_parts = [diagram_type, "diagram"]
        if specific_feature:
            query_parts.append(specific_feature)
        query_parts.append("syntax")

        query = " ".join(query_parts)

        return self._search_plantuml_docs(query, tokens=3000)

    def _search_plantuml_docs(self, query: str, tokens: int = 5000) -> str:
        """
        Internal helper method to search PlantUML documentation.
        """
        try:
            if self.upstash_plantuml_tool is None:
                error_msg = "Error: Could not find get-library-docs tool in Context7 MCP server."
                self._save_query_result(query, error_msg, tokens)
                return error_msg

            # Call the documentation tool with PlantUML specific parameters
            result = self.upstash_plantuml_tool.invoke({
                "context7CompatibleLibraryID": self.plantuml_library_id,
                "tokens": tokens,
                "topic": query
            })

            # Save the query and result
            self._save_query_result(query, result, tokens)

            return result

        except Exception as e:
            error_msg = f"Error searching PlantUML documentation: {str(e)}"
            self._save_query_result(query, error_msg, tokens)
            return error_msg

    def _save_query_result(self, query: str, result: str, tokens: int):
        """
        Save the query and result to the log file.

        Args:
            query: The search query
            result: The result returned by the tool
            tokens: The number of tokens requested
        """
        try:
            # Create log entry
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "query": query,
                "tokens_requested": tokens,
                "result": result,
                "library_id": self.plantuml_library_id
            }

            # Read existing log file or create new one
            if os.path.exists(self.log_file):
                try:
                    with open(self.log_file, 'r', encoding='utf-8') as f:
                        logs = json.load(f)
                        if not isinstance(logs, list):
                            logs = [logs]  # Handle single entry case
                except (json.JSONDecodeError, FileNotFoundError):
                    logs = []
            else:
                logs = []

            # Add new entry
            logs.append(log_entry)

            # Write back to file
            with open(self.log_file, 'w', encoding='utf-8') as f:
                json.dump(logs, f, indent=2, ensure_ascii=False)

        except Exception as e:
            # If logging fails, don't break the main functionality
            print(f"Warning: Failed to save query log: {e}")

    def get_tools(self):
        """
        Get the tool instances for use in agent tool lists.

        Returns:
            List of tool instances that can be used by LangChain agents
        """
        @tool("plantuml_documentation_search")
        def search_doc(query: str, tokens: Optional[int] = 5000) -> str:
            """Search PlantUML documentation and syntax reference."""
            return self.plantuml_documentation_search(query, tokens)

        @tool("plantuml_syntax_lookup")
        def lookup_syntax(diagram_type: str, specific_feature: Optional[str] = None) -> str:
            """Get specific PlantUML syntax for diagram types and features."""
            return self.plantuml_syntax_lookup(diagram_type, specific_feature)

        return [search_doc, lookup_syntax]
