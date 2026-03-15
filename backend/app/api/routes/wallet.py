from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.wallet import ShopPurchaseResponse, WalletResponse, WalletTransactionResponse
from app.services.wallet_service import buy_streak_freeze, get_inventory, get_transaction_history
from app.services.xp_service import get_or_create_progress

router = APIRouter(tags=["wallet"])


@router.get("/api/wallet", response_model=WalletResponse)
async def get_wallet(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> WalletResponse:
    """Get wallet balance, freeze tokens, and transaction history."""
    progress = await get_or_create_progress(db, user.id)
    inventory = await get_inventory(db, user.id)
    transactions = await get_transaction_history(db, user.id, limit=30)

    return WalletResponse(
        balance=progress.coins_balance,
        freeze_tokens=inventory.get("streak_freeze", 0),
        transactions=[WalletTransactionResponse.model_validate(t) for t in transactions],
    )


@router.post("/api/shop/streak-freeze", response_model=ShopPurchaseResponse)
async def purchase_streak_freeze(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ShopPurchaseResponse:
    """Buy a streak freeze token for 50 coins."""
    result = await buy_streak_freeze(db, user.id)
    await db.commit()
    return ShopPurchaseResponse(**result)
