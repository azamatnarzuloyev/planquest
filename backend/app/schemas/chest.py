import datetime as dt
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel


class ChestResponse(BaseModel):
    id: UUID
    type: str
    rarity: str
    status: str
    source: str
    created_at: dt.datetime

    model_config = {"from_attributes": True}


class ChestOpenResponse(BaseModel):
    chest: ChestResponse
    loot: dict[str, Any]
