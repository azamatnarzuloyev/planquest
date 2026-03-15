from pydantic import BaseModel

from app.schemas.task import TaskResponse


class TaskCompleteResponse(BaseModel):
    task: TaskResponse
    xp_awarded: int
    total_xp: int
    leveled_up: bool
    new_level: int
    coins_earned: int


class UserProgressResponse(BaseModel):
    current_level: int
    total_xp: int
    xp_for_next_level: int
    xp_progress_in_level: int
    progress_percent: float
    coins_balance: int

    model_config = {"from_attributes": True}
