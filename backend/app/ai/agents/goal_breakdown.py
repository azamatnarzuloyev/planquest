"""Goal Breakdown Agent — decomposes goals into milestones and tasks."""

from pydantic import BaseModel

from app.ai.agents.base import BaseAgent
from app.ai.prompts.goal_breakdown import GOAL_BREAKDOWN_SYSTEM_PROMPT
from app.ai.schemas.goals import GoalDecomposition
from app.config import settings


class GoalBreakdownAgent(BaseAgent):
    name = "goal_breakdown"
    model = settings.AI_MODEL_DEFAULT
    max_tokens = 2048

    def get_system_prompt(self) -> str:
        return GOAL_BREAKDOWN_SYSTEM_PROMPT

    def build_user_message(self, context: dict) -> str:
        parts = []
        parts.append(f"Goal: {context.get('goal_title', '')}")

        if context.get("goal_description"):
            parts.append(f"Description: {context['goal_description']}")

        if context.get("target_date"):
            parts.append(f"Deadline: {context['target_date']}")

        if context.get("category"):
            parts.append(f"Category: {context['category']}")

        parts.append(f"User segment: {context.get('segment', 'other')}")
        parts.append(f"User level: {context.get('current_level', 1)}")
        parts.append(f"Avg tasks/day: {context.get('avg_tasks_per_day', 3)}")

        parts.append("\nBreak this goal into weekly milestones with daily tasks.")
        parts.append("Keep it concise: max 4 milestones, max 4 tasks per milestone.")
        parts.append("Return JSON.")
        return "\n".join(parts)

    def get_output_schema(self) -> type[BaseModel]:
        return GoalDecomposition
