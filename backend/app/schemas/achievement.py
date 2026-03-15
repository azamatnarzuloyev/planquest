import datetime as dt
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class AchievementResponse(BaseModel):
    id: UUID
    key: str
    name: str
    description: str
    category: str
    icon: str
    requirement_type: str
    requirement_value: int
    reward_xp: int
    reward_coins: int
    # User progress (filled per-user)
    progress: int = 0
    unlocked: bool = False
    unlocked_at: Optional[dt.datetime] = None
