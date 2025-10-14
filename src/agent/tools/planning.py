"""Planning middleware with task management, and persistent scratchpad functionality."""
from typing import Awaitable, Callable, Optional, Annotated, NotRequired
from langchain.agents.middleware import PlanningMiddleware
from langchain.agents.middleware.planning import PlanningState
from langchain.agents.middleware.types import (
    ModelCallResult,
    ModelRequest,
    ModelResponse,
)
from langchain_core.messages import ToolMessage
from langchain_core.tools import tool, InjectedToolCallId
from langgraph.store.base import BaseStore
from langgraph.types import Command


class PersistentPlanningState(PlanningState):
    """State that extends PlanningState to include a scratchpad field.

    The scratchpad provides temporary storage during agent execution,
    allowing information to persist within a single conversation thread.
    """
    scratchpad: NotRequired[str]


class PersistentPlanningMiddleware(PlanningMiddleware):
    """Extended planning middleware with persistent scratchpad functionality.

    This middleware combines task management capabilities with persistent scratchpad
    storage, allowing agents to maintain context across conversation threads.

    Args:
        store: Persistent store for cross-thread memory (e.g., InMemoryStore)
        namespace: Tuple namespace for organizing stored data
        system_prompt: Custom system prompt for task management
        tool_description: Custom description for the write_todos tool
    """

    state_schema = PersistentPlanningState

    def __init__(
        self,
        store: Optional[BaseStore] = None,
        namespace: tuple = ("agent", "scratchpad"),
        **kwargs
    ):
        super().__init__(**kwargs)
        self.store = store
        self.namespace = namespace
        self.current_scratchpad = ""  # In-memory cache of current scratchpad

        @tool(
            name_or_callable="write_to_scratchpad",
            description="Save notes to the scratchpad for future reference within the conversation."
        )
        def write_to_scratchpad(
            notes: str,
            tool_call_id: Annotated[str, InjectedToolCallId]
        ) -> Command:
            """Save notes to the scratchpad."""


            # Update in-memory cache
            self.current_scratchpad = notes

            # Save to persistent store if available
            if self.store:
                # This will overwrite existing notes
                # consider if we want append functionality in the future
                self.store.put(self.namespace, "scratchpad", {"scratchpad": notes})

            # Update in-memory state, clear messages context offload
            update = {"scratchpad": notes, "messages": []}
            update["messages"].append(
                ToolMessage(
                    content=f"Wrote to scratchpad: {notes}",
                    tool_call_id=tool_call_id
                )
            )

            return Command(update=update)

        @tool(
            name_or_callable="read_from_scratchpad",
            description="Read previously saved notes from the scratchpad."
        )
        def read_from_scratchpad(
            tool_call_id: Annotated[str, InjectedToolCallId]
        ) -> Command:
            """Read notes from the scratchpad."""
            notes = ""


            if self.store:
                stored_data = self.store.get(self.namespace, "scratchpad")
                if stored_data:
                    notes = stored_data.value.get("scratchpad", "")
            # Fallback to in-memory cache
            if not notes and self.current_scratchpad:
                notes = self.current_scratchpad

            # Fallback message if no notes found
            if not notes:
                notes = "No notes found in scratchpad"

            return Command(
                update={
                    "messages": [
                        ToolMessage(
                            content=f"Notes from scratchpad: {notes}",
                            tool_call_id=tool_call_id
                        )
                    ]
                }
            )

        self.tools.extend([write_to_scratchpad, read_from_scratchpad])

    async def awrap_model_call(
        self,
        request: ModelRequest,
        handler: Callable[[ModelRequest], Awaitable[ModelResponse]],
    ) -> ModelCallResult:
        """Asynchronously update the system prompt to include the todo system prompt."""
        request.system_prompt = (
            request.system_prompt + "\n\n" + self.system_prompt
            if request.system_prompt
            else self.system_prompt
        )
        return await handler(request)
