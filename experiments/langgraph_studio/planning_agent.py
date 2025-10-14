"""A planning agent that uses a state graph to manage conversation state."""
import random
from typing import NotRequired, Literal, Annotated
from langgraph.graph import StateGraph, START, END
from langgraph.types import (interrupt, Command)
from langchain.agents import create_agent, AgentState
from experiments.langgraph_studio.util import github_clone

class State(AgentState):
    """ State for the planning agent """
    plan: NotRequired[Annotated[list[str], "multiple"]]

def human_approval(state: State) -> Command[Literal["agent", "replan"]]:
    """Ask human for approval of the plan."""
    is_approved = interrupt(
        {
            "question": "Does this look correct?",
            "plan": state.get("plan", None),
        }
    )
    if is_approved:
        return Command(goto="agent")
    return Command(goto="replan")

def update_plan(state: State) -> State:
    """Update the plan based on new information."""
    if "plan" not in state or state["plan"] is None:
        state["plan"] = ["Step 1: Initial Step"]
    state["plan"].append(
        f"Step {len(state['plan']) + 1}: {(state.get('messages', [])[-1]).content}")
    return state

def replan(state: State) -> State:
    """Modify the plan if not approved."""
    state["plan"] = ["Step 1: Gather more information", "Step 2: Provide detailed response"]
    return state



agent = create_agent(
    "openai:gpt-4.1-nano",
    tools=[github_clone],
    system_prompt="Act as an customer support agent."
    # post_model_hook=update_plan, # should be implemented in middleware
)

graph_builder = StateGraph(State)
graph_builder.add_node("human_approval", human_approval)
graph_builder.add_node("replan", replan)
graph_builder.add_node("agent", agent)

graph_builder.add_edge(START, "agent")
graph_builder.add_edge("agent", END)
graph_builder.add_edge("agent", "human_approval")
graph_builder.add_edge("human_approval", "agent")
graph_builder.add_edge("human_approval", "replan")
graph_builder.add_conditional_edges(
    "agent",
    lambda state: "replan" if state.get("plan") is None
        else (END if random.random() < 0.5 else "replan"),
    {
        "replan": "replan",
        END: END
    }
)

graph_builder.add_edge("replan", "agent")
planning_agent = graph_builder.compile()
