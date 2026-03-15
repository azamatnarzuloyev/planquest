import datetime as dt
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class MissionResponse(BaseModel):
    id: UUID
    type: str
    difficulty: str
    title: str
    description: str
    action: str
    target_value: int
    current_value: int
    reward_xp: int
    reward_coins: int
    status: str
    assigned_date: dt.date
    completed_at: Optional[dt.datetime]

    model_config = {"from_attributes": True}
