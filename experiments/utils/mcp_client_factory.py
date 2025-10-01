"""
MCP Client Factory provides utilities for managing MCP (Model Context Protocol) server
configurations and creating MCP clients. It handles loading and saving configuration
data from JSON files and provides a factory function for creating MultiServerMCPClient
instances.

Key Features:
- Load MCP server configurations from JSON files
- Save MCP server configurations to JSON files
- Create MultiServerMCPClient instances from saved configurations

Usage:
    client = create_mcp_client_from_config()
    mcp_tools = await client.get_tools()
    tools += mcp_tools
"""

import json
import os
from typing import Dict
from langchain_mcp_adapters.client import MultiServerMCPClient


# Config file path
MCP_CONFIG_FILE = "mcp_servers_config.json"

def load_mcp_config(path:str = MCP_CONFIG_FILE) -> Dict[str, Dict[str,str]]:

    """Load MCP server configuration from file."""
    if not os.path.exists(path):
        with open(path, 'w', encoding='utf-8') as f:
            json.dump({}, f)
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_mcp_config(config: Dict[str, Dict[str, str]], path:str = MCP_CONFIG_FILE) -> None:
    """Save MCP server configuration to file."""
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2)

def create_mcp_client_from_config() -> MultiServerMCPClient:
    """Create a MultiServerMCPClient from the saved configuration."""
    config = load_mcp_config()
    return MultiServerMCPClient(config)
