"""Base provider interface for LLM calls."""

from abc import ABC, abstractmethod


class BaseProvider(ABC):
    @abstractmethod
    async def call(
        self,
        system_prompt: str,
        user_message: str,
        model: str | None = None,
        max_tokens: int = 1024,
        temperature: float = 0.7,
    ) -> dict:
        """Call the LLM and return parsed response.

        Returns:
            {
                "content": str,          # raw text response
                "input_tokens": int,
                "output_tokens": int,
                "model": str,
            }
        """
        ...

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the provider is available."""
        ...
