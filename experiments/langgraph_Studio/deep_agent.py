"""A deep agent that uses tools to perform software architecture reconstruction."""
from util import get_today_str, think_tool, github_clone
from prompts import SUBAGENT_USAGE_INSTRUCTIONS, RESEARCHER_INSTRUCTIONS
from deepagents import create_deep_agent, SubAgent

sub_agent_tools = [think_tool, github_clone]
research_sub_agent = SubAgent({
    "name": "research-agent",
    "description": "Delegate research to the sub-agent researcher. "
    "Only give this researcher one topic at a time.",
    "prompt": RESEARCHER_INSTRUCTIONS.format(date=get_today_str()),
    "tools": sub_agent_tools,
    "model": {"model": "gpt-5-nano","model_provider": "openai"},
})

max_concurrent_research_units = 3
max_researcher_iterations = 3
SUBAGENT_INSTRUCTIONS = SUBAGENT_USAGE_INSTRUCTIONS.format(
    max_concurrent_research_units=max_concurrent_research_units,
    max_researcher_iterations=max_researcher_iterations,
    date=get_today_str(),
)


tools = [think_tool, github_clone]
deep_agent = create_deep_agent(
    tools=tools,
    # instructions=SUBAGENT_INSTRUCTIONS,
    model="openai:gpt-5-nano",
    subagents=[research_sub_agent],
)
graph = deep_agent
