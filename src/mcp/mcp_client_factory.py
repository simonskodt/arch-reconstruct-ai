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
import sys
from typing import Any, Dict, Optional, Match
from langchain_mcp_adapters.client import MultiServerMCPClient
from dotenv import load_dotenv
from .utils import utils_configurations
from .utils._sanitize import ConfigSanitizer


def load_mcp_config(
        path: str = utils_configurations.MCP_CONFIG_FILE,
    ) -> Dict[str, Any]:
    """
    Load MCP server configuration from a JSON file.

    Args:
        path: Path to the configuration file

    Returns:
        Dictionary containing the MCP server configuration
    """
    if not os.path.exists(path):
        with open(path, 'w', encoding='utf-8') as f:
            json.dump({}, f)

    with open(path, 'r', encoding='utf-8') as f:
        config = json.load(f)

    return config

def save_mcp_config(
    config: Dict[str, Dict[str, Any]],
    path: str = utils_configurations.MCP_CONFIG_FILE
) -> Dict[str, str]:
    """
    Save MCP server configuration to file with secret redaction.
        config: The configuration dictionary to save
        path: Path where to save the configuration file

    Returns:
        Status dictionary indicating success or warning with redaction details
    """
    sanitizer = ConfigSanitizer()
    sanitized_config = sanitizer.sanitize(config)
    leaks = sanitizer.leaks

    with open(path, 'w', encoding='utf-8') as f:
        json.dump(sanitized_config, f, indent=2)

    if leaks:
        unique = sorted(set(leaks))
        return {
            "Status": "Warning",
            "Message":
                f"Potential secret values detected and redacted in the following config paths: "
                f"{', '.join(unique)}. Values have been redacted in the saved file."
        }

    return {"Status": "Success", "Message": f"Configuration saved successfully at: {path}"}


def create_mcp_client_from_config(
        path: str = utils_configurations.MCP_CONFIG_FILE,
        env: Optional[str] = None
    ) -> MultiServerMCPClient:
    """
    Create a MultiServerMCPClient from the saved configuration with env variable substitution.

    Args:
        path: Path to the configuration file
        env: Path to environment file for variable substitution

    Returns:
        Configured MultiServerMCPClient instance
    """
    config = load_mcp_config(path)
    config = _load_cfg_with_environment(config, env)
    return MultiServerMCPClient(config)

def _load_cfg_with_environment(config: Dict[str, Any], env: Optional[str]) -> Dict[str, Any]:
    """
    Substitute environment variables in configuration strings.

    Args:
        config: Configuration dictionary
        env: Path to environment file

    Returns:
        Configuration with environment variables resolved
    """
    load_dotenv(env)
    return _resolve(config)

def _resolve(obj) -> Any:
    """
    Recursively resolve environment variables in configuration strings.

    Args:
        obj: Configuration object (dict, list, or str)

    Returns:
        Object with environment variables substituted
    """
    # Find ALL-CAPS tokens (letters, digits, underscores, must contain at least one letter)
    if isinstance(obj, dict):
        for key, value in obj.items():
            obj[key] = _resolve(value)
        return obj

    if isinstance(obj, list):
        return [_resolve(item) for item in obj]

    if isinstance(obj, str):
        return utils_configurations.ENVIRONMENT_VARIABLE_REGEX.sub(_replace, obj)
    return obj

def _replace(match: Match[str]) -> str:
    """
    Replace a matched environment variable with its value.

    Args:
        match: Regex match object containing the variable name

    Returns:
        The environment variable value

    Raises:
        ValueError: If the environment variable is not set
    """
    name = match.group(0)
    value = os.getenv(name)
    if value is None:
        raise ValueError(f"Missing environment variable: {name}")
    return value

if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "--config":
        test_config = json.loads(sys.argv[2])
        try:
            result = save_mcp_config(test_config)
            print("Save successful:", result)
            cfg = load_mcp_config()
            print("Load successful:", cfg)
        except ValueError as e:
            print("Loading failed:", e)
    else:
        print("Usage: python mcp_client_factory.py --config '<json_config>'")