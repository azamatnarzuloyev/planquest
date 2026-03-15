"""Base agent class for all specialized AI agents."""

import json
import logging
from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel

from app.ai.providers.openai_provider import get_openai_provider

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Abstract base for all PlanQuest AI agents."""

    name: str = "base"
    model: str | None = None  # None = use default
    max_tokens: int = 1024

    @abstractmethod
    def get_system_prompt(self) -> str:
        """Return the system prompt for this agent."""
        ...

    @abstractmethod
    def build_user_message(self, context: dict) -> str:
        """Build the user message from context."""
        ...

    @abstractmethod
    def get_output_schema(self) -> type[BaseModel]:
        """Return the Pydantic model for output validation."""
        ...

    async def run(self, context: dict) -> tuple[Any, dict]:
        """Execute the agent: build prompt → call LLM → validate → return.

        Returns: (validated_output, metadata)
        """
        provider = get_openai_provider()

        system_prompt = self.get_system_prompt()
        user_message = self.build_user_message(context)

        parsed, metadata = await provider.call_json(
            system_prompt=system_prompt,
            user_message=user_message,
            model=self.model,
            max_tokens=self.max_tokens,
        )

        # Validate with Pydantic schema
        schema = self.get_output_schema()
        validated = schema.model_validate(parsed)

        metadata["agent"] = self.name
        return validated, metadata
