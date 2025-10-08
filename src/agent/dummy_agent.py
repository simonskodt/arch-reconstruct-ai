"""
This file defines a barebones agent.
"""
from langchain.agents import create_agent

MODEL = "openai:gpt-4.1-nano"

agent = create_agent(
    MODEL,
    tools=[],
    prompt="You are a helpful assistant.",
)
