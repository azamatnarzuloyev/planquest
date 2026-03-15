import datetime as dt
from uuid import UUID

from pydantic import BaseModel


class WalletTransactionResponse(BaseModel):
    id: UUID
    amount: int
    type: str
    source: str
    description: str
    created_at: dt.datetime

    model_config = {"from_attributes": True}


class WalletResponse(BaseModel):
    balance: int
    freeze_tokens: int
    transactions: list[WalletTransactionResponse]


class ShopPurchaseResponse(BaseModel):
    ok: bool
    error: str | None = None
    balance: int
    freeze_tokens: int = 0
