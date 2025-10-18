"""
This file defines a barebones agent.
"""
import os
import sys
from langchain.agents import create_agent
from langchain.agents.middleware.summarization import SummarizationMiddleware


# NECESSARY: In order to enable imports from local modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
# pylint: disable=wrong-import-position
from src.utils.services import check_service_availability

# tools
from src.agent.tools.drawing import get_drawing_tools
from src.agent.tools.github import (
    git_clone_tool,
    extract_repository_details,
    load_extracted_repository
)

check_service_availability()

tools = [
    git_clone_tool,
    extract_repository_details,
    load_extracted_repository,
] + get_drawing_tools()


MODEL = "openai:gpt-{number}-nano"
summarization_tool = SummarizationMiddleware(MODEL.format(number="4.1"),
                                             max_tokens_before_summary=5000,
                                             messages_to_keep=5)

agent = create_agent(
    MODEL.format(number="5"),
    tools=tools,
    system_prompt="You are a helpful assistant.",
    middleware=[summarization_tool],
)
