"""Deterministic routing — maps request types to agents."""

from app.ai.agents.base import BaseAgent
from app.ai.agents.coaching import CoachingAgent
from app.ai.agents.goal_breakdown import GoalBreakdownAgent
from app.ai.agents.mission_design import MissionDesignAgent
from app.ai.agents.motivation import MotivationCopyAgent
from app.ai.agents.planner import PlannerAgent
from app.ai.agents.questions import QuestionAgent
from app.ai.agents.recovery import RecoveryAgent

# Agent registry — 7 agents
_AGENT_REGISTRY: dict[str, type[BaseAgent]] = {
    "questions": QuestionAgent,
    "daily_plan": PlannerAgent,
    "goal_breakdown": GoalBreakdownAgent,
    "recovery": RecoveryAgent,
    "coaching": CoachingAgent,
    "mission_design": MissionDesignAgent,
    "motivation": MotivationCopyAgent,
}


def register_agent(request_type: str, agent_class: type[BaseAgent]) -> None:
    """Register an agent for a request type."""
    _AGENT_REGISTRY[request_type] = agent_class


def get_agent(request_type: str) -> BaseAgent:
    """Get agent instance for request type."""
    agent_class = _AGENT_REGISTRY.get(request_type)
    if agent_class is None:
        raise ValueError(f"No agent registered for request type: {request_type}")
    return agent_class()


def get_available_agents() -> list[str]:
    """List all registered request types."""
    return list(_AGENT_REGISTRY.keys())
