"""Conversational Planner — chat-style planning through natural dialogue."""

import json
import logging
import time as _time

from app.ai.prompts.conversational_planner import CONVERSATIONAL_PLANNER_PROMPT
from app.ai.providers.openai_provider import get_openai_provider
from app.config import settings

logger = logging.getLogger(__name__)


async def chat_plan(messages: list[dict], user_context: dict, force_plan: bool = False) -> tuple[dict, dict]:
    """Send conversation to AI, get question or plan.

    Args:
        messages: conversation history
        user_context: user data
        force_plan: if True, AI must return plan (no more questions)
    """
    provider = get_openai_provider()

    system = CONVERSATIONAL_PLANNER_PROMPT + f"\n\nFOYDALANUVCHI KONTEKSTI:\n{_format_context(user_context)}"

    if force_plan:
        system += "\n\nMUHIM: Foydalanuvchi yakunlashni so'radi. Hozir mavjud ma'lumotlar asosida REJA YARAT. type: 'plan' qaytar. Savol BERMA."

    api_messages = [{"role": "system", "content": system}]
    for m in messages:
        api_messages.append({"role": m["role"], "content": m["content"]})

    start = _time.monotonic()
    response = await provider.client.chat.completions.create(
        model=settings.AI_MODEL_DEFAULT,
        messages=api_messages,
        max_tokens=1024,
        temperature=0.7,
        response_format={"type": "json_object"},
    )
    latency = int((_time.monotonic() - start) * 1000)

    content = response.choices[0].message.content or ""
    usage = response.usage
    user_count = sum(1 for m in messages if m["role"] == "user")

    logger.info(f"Chat plan: user_msgs={user_count} force={force_plan} in={usage.prompt_tokens if usage else 0} out={usage.completion_tokens if usage else 0} latency={latency}ms")

    # Parse
    try:
        parsed = json.loads(content)
    except json.JSONDecodeError:
        try:
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            parsed = json.loads(content)
        except (json.JSONDecodeError, IndexError):
            parsed = {"type": "question", "message": content[:100], "suggestions": []}

    metadata = {
        "input_tokens": usage.prompt_tokens if usage else 0,
        "output_tokens": usage.completion_tokens if usage else 0,
        "model": settings.AI_MODEL_DEFAULT,
        "latency_ms": latency,
    }

    return parsed, metadata


def _format_context(ctx: dict) -> str:
    parts = []
    if ctx.get("segment"): parts.append(f"Segment: {ctx['segment']}")
    if ctx.get("streak_current"): parts.append(f"Streak: {ctx['streak_current']} kun")
    if ctx.get("current_level"): parts.append(f"Level: {ctx['current_level']}")

    tasks = ctx.get("pending_tasks", [])
    if tasks:
        parts.append(f"Bugungi tasklar ({len(tasks)}):")
        for t in tasks[:10]:
            mins = f" [{t.get('estimated_minutes', '')}m]" if t.get("estimated_minutes") else ""
            parts.append(f"  - {t.get('title', '')}{mins}")

    habits = ctx.get("habits", [])
    if habits:
        done = sum(1 for h in habits if h.get("today_completed"))
        parts.append(f"Habitlar: {done}/{len(habits)} bajarilgan")

    if ctx.get("focus_today_minutes"):
        parts.append(f"Bugungi fokus: {ctx['focus_today_minutes']} min")

    return "\n".join(parts) if parts else "Yangi foydalanuvchi."
