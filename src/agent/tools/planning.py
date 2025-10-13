"""add planning middleware to agents for task management and organization."""
from typing import  Awaitable, Callable
from langchain.agents.middleware import PlanningMiddleware
from langchain.agents.middleware.types import ModelCallResult, ModelRequest, ModelResponse

class AsyncPlanningMiddleware(PlanningMiddleware):
    """Async wrapper for PlanningMiddleware that properly handles async model calls."""

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
