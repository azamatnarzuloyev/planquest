"""Business rule validation for AI outputs."""

from app.ai.schemas.missions import MissionSuggestions, SuggestedMission

# Bounds
MISSION_XP_MIN = 10
MISSION_XP_MAX = 100
MISSION_COINS_MIN = 5
MISSION_COINS_MAX = 50
VALID_ACTIONS = {"tasks_completed", "habits_logged", "focus_minutes", "focus_sessions"}


def validate_mission_suggestions(suggestions: MissionSuggestions) -> tuple[MissionSuggestions, list[str]]:
    """Validate and clamp AI mission suggestions within allowed bounds.

    Returns: (clamped_suggestions, warnings)
    """
    warnings = []
    clamped = []

    for m in suggestions.suggested_missions:
        if m.action not in VALID_ACTIONS:
            warnings.append(f"Invalid action '{m.action}' — skipped")
            continue

        # Clamp rewards
        xp = max(MISSION_XP_MIN, min(MISSION_XP_MAX, m.reward_xp))
        coins = max(MISSION_COINS_MIN, min(MISSION_COINS_MAX, m.reward_coins))

        if xp != m.reward_xp:
            warnings.append(f"XP clamped: {m.reward_xp} → {xp}")
        if coins != m.reward_coins:
            warnings.append(f"Coins clamped: {m.reward_coins} → {coins}")

        clamped.append(SuggestedMission(
            title=m.title,
            description=m.description,
            action=m.action,
            target_value=max(1, min(50, m.target_value)),
            difficulty=m.difficulty,
            reward_xp=xp,
            reward_coins=coins,
        ))

    return MissionSuggestions(suggested_missions=clamped), warnings
