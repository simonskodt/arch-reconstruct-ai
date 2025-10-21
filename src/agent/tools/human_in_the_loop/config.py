"""Configuration for human-in-the-loop"""
from langchain.agents.middleware.human_in_the_loop import InterruptOnConfig
DEFAULT_INTERRUPT_DESCRIPTION = "Review the tool call."
DefaultInterruptConfig = InterruptOnConfig(
    allowed_decisions=["approve", "reject"],
    description=DEFAULT_INTERRUPT_DESCRIPTION,
)
