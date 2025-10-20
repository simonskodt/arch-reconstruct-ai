"""Configuration for human-in-the-loop"""
from langchain.agents.middleware.human_in_the_loop import InterruptOnConfig
DEFAULT_INTERRUPT_DESCRIPTION = "Review the tool call."
DEFAULT_INTERRUPT_CONFIG = InterruptOnConfig(
    allowed_decisions=["approve", "reject"],
    description=DEFAULT_INTERRUPT_DESCRIPTION,
)
