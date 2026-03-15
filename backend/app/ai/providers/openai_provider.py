"""OpenAI API provider with retry and error handling."""

import asyncio
import json
import logging
import time

from openai import AsyncOpenAI, APIError, APITimeoutError, RateLimitError

from app.ai.providers.base import BaseProvider
from app.config import settings

logger = logging.getLogger(__name__)

MAX_RETRIES = 1
RETRY_DELAY = 2.0
TIMEOUT = 30


class OpenAIProvider(BaseProvider):
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,
            timeout=TIMEOUT,
        ) if settings.OPENAI_API_KEY else None
        self.default_model = settings.AI_MODEL_DEFAULT

    async def call(
        self,
        system_prompt: str,
        user_message: str,
        model: str | None = None,
        max_tokens: int = 1024,
        temperature: float = 0.7,
    ) -> dict:
        if self.client is None:
            raise RuntimeError("OpenAI API key not configured")

        use_model = model or self.default_model
        last_error = None

        for attempt in range(MAX_RETRIES + 1):
            try:
                start = time.monotonic()
                response = await self.client.chat.completions.create(
                    model=use_model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_message},
                    ],
                    max_tokens=max_tokens,
                    temperature=temperature,
                    response_format={"type": "json_object"},
                )
                latency = int((time.monotonic() - start) * 1000)

                content = response.choices[0].message.content or ""
                usage = response.usage

                logger.info(
                    f"OpenAI call: model={use_model} "
                    f"in={usage.prompt_tokens} out={usage.completion_tokens} "
                    f"latency={latency}ms attempt={attempt}"
                )

                return {
                    "content": content,
                    "input_tokens": usage.prompt_tokens if usage else 0,
                    "output_tokens": usage.completion_tokens if usage else 0,
                    "model": use_model,
                    "latency_ms": latency,
                    "retry_count": attempt,
                }

            except (APITimeoutError, APIError) as e:
                last_error = e
                if attempt < MAX_RETRIES:
                    logger.warning(f"OpenAI retry {attempt+1}: {e}")
                    await asyncio.sleep(RETRY_DELAY)
                else:
                    logger.error(f"OpenAI failed after {MAX_RETRIES+1} attempts: {e}")

            except RateLimitError as e:
                logger.error(f"OpenAI rate limited: {e}")
                raise

        raise RuntimeError(f"OpenAI provider failed: {last_error}")

    async def call_json(
        self,
        system_prompt: str,
        user_message: str,
        model: str | None = None,
        max_tokens: int = 1024,
        temperature: float = 0.7,
    ) -> tuple[dict, dict]:
        """Call and parse JSON response. Returns (parsed_json, metadata)."""
        result = await self.call(system_prompt, user_message, model, max_tokens, temperature)
        content = result["content"]

        try:
            parsed = json.loads(content)
        except json.JSONDecodeError:
            # Try to extract JSON from markdown code blocks
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
                parsed = json.loads(content)
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
                parsed = json.loads(content)
            else:
                raise ValueError(f"Failed to parse JSON from response: {content[:200]}")

        metadata = {
            "input_tokens": result["input_tokens"],
            "output_tokens": result["output_tokens"],
            "model": result["model"],
            "latency_ms": result["latency_ms"],
            "retry_count": result["retry_count"],
        }
        return parsed, metadata

    async def health_check(self) -> bool:
        if self.client is None:
            return False
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": "ping"}],
                max_tokens=5,
            )
            return bool(response.choices)
        except Exception as e:
            logger.error(f"OpenAI health check failed: {e}")
            return False


# Singleton
_provider: OpenAIProvider | None = None


def get_openai_provider() -> OpenAIProvider:
    global _provider
    if _provider is None:
        _provider = OpenAIProvider()
    return _provider
