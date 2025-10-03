"""A deep agent that uses tools to perform software architecture reconstruction."""
from util import get_today_str, think_tool
from prompts import SUBAGENT_USAGE_INSTRUCTIONS, RESEARCHER_INSTRUCTIONS
from deepagents import create_deep_agent, SubAgent

sub_agent_tools = [think_tool]
research_sub_agent = SubAgent({
    "name": "research-agent",
    "description": "Delegate research to the sub-agent researcher. "
    "Only give this researcher one topic at a time.",
    "prompt": RESEARCHER_INSTRUCTIONS.format(date=get_today_str()),
    "tools": sub_agent_tools,
    "model": {"model": "gpt-5-nano", "model_provider": "openai"},
})

MAX_CONCURRENT_RESEARCH_UNITS = 3
MAX_RESEARCHER_ITERATIONS = 3
SUBAGENT_INSTRUCTIONS = SUBAGENT_USAGE_INSTRUCTIONS.format(
    max_concurrent_research_units=MAX_CONCURRENT_RESEARCH_UNITS,
    max_researcher_iterations=MAX_RESEARCHER_ITERATIONS,
    date=get_today_str(),
)


tools = [think_tool]
deep_agent = create_deep_agent(
    tools=tools,
    # instructions=SUBAGENT_INSTRUCTIONS,
    model="openai:gpt-5-nano",
    subagents=[research_sub_agent],
)
graph = deep_agent
