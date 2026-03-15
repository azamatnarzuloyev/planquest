"""Validate AI-generated daily plans against business rules."""

from app.ai.schemas.plans import DailyPlan


def validate_plan(plan: DailyPlan) -> tuple[bool, list[str], list[str]]:
    """Validate a daily plan.

    Returns: (is_valid, errors, warnings)
    """
    errors = []
    warnings = []

    # Check time blocks
    total_minutes = 0
    for i, block in enumerate(plan.time_blocks):
        # Parse times
        try:
            start_h, start_m = map(int, block.start.split(":"))
            end_h, end_m = map(int, block.end.split(":"))
        except (ValueError, AttributeError):
            errors.append(f"Block {i}: invalid time format")
            continue

        # Check range 06:00-23:00
        if start_h < 6 or end_h > 23:
            warnings.append(f"Block {i}: time outside 06:00-23:00")

        # Check end > start
        start_total = start_h * 60 + start_m
        end_total = end_h * 60 + end_m
        if end_total <= start_total:
            errors.append(f"Block {i}: end time must be after start time")
            continue

        duration = end_total - start_total
        total_minutes += duration

        # Check block duration reasonable
        if duration > 180:
            warnings.append(f"Block {i}: very long block ({duration} min)")

    # Max 10 hours scheduled
    if total_minutes > 600:
        warnings.append(f"Total scheduled time: {total_minutes} min (over 10 hours)")

    # Max 15 task blocks
    task_blocks = [b for b in plan.time_blocks if b.type == "task"]
    if len(task_blocks) > 15:
        errors.append(f"Too many task blocks: {len(task_blocks)} (max 15)")

    # Max 5 focus sessions
    focus_blocks = [b for b in plan.time_blocks if b.type == "focus_session"]
    if len(focus_blocks) > 5:
        warnings.append(f"Many focus sessions: {len(focus_blocks)}")

    # Max 3 suggested tasks
    if len(plan.suggested_new_tasks) > 3:
        errors.append(f"Too many suggested tasks: {len(plan.suggested_new_tasks)} (max 3)")

    is_valid = len(errors) == 0
    return is_valid, errors, warnings
