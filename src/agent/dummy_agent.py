"""
This file defines a barebones agent.
"""
import asyncio
from langchain.agents import create_agent
from src.agent.tools.github import git_clone_tool
from src.agent.tools.human_in_the_loop import add_human_in_the_loop, weather_tool
from src.mcp.mcp_client_factory import create_mcp_client_from_config


mcp_client = create_mcp_client_from_config()
mcp_tools = asyncio.run(mcp_client.get_tools())

tools = [git_clone_tool, weather_tool]
combine_tools = tools + mcp_tools

# MODEL = "openai:gpt-4.1-nano"
# agent = create_agent(
#     MODEL,
#     tools=combine_tools,
#     prompt="You are a helpful assistant.",

# )
print("Available tools:")
weather_tool2 = add_human_in_the_loop(weather_tool)
agent = create_agent(
    "openai:gpt-4.1-nano",
    tools=[weather_tool],
    prompt="Your are a helpful assistant.",
)
