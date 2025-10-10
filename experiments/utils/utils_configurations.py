"""Utility configurations including constants and regex patterns for the experiments utils."""

import re

# Regex pattern for matching environment variable names (ALL_CAPS with at least one letter)
ENVIRONMENT_VARIABLE_REGEX = re.compile(r'\b(?=[A-Z0-9_]*[A-Z])[A-Z0-9_]+\b')

# Default filename for MCP server configuration
MCP_CONFIG_FILE = "mcp_servers_config.json"
