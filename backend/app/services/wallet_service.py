"""Wallet and shop service — coin transactions and item purchases."""

from uuid import UUID

from sqlalchemy import and_, desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user_progress import UserProgress
from app.models.wallet import RewardsInventory, WalletTransaction

STREAK_FREEZE_COST = 50


async def log_transaction(
    db: AsyncSession,
    user_id: UUID,
    amount: int,
    tx_type: str,
    source: str,
    description: str = "",
) -> WalletTransaction:
    """Log a coin transaction (earn or spend)."""
    tx = WalletTransaction(
        user_id=user_id,
        amount=amount,
        type=tx_type,
        source=source,
        description=description,
    )
    db.add(tx)
    await db.flush()
    return tx


async def get_transaction_history(
    db: AsyncSession, user_id: UUID, limit: int = 50
) -> list[WalletTransaction]:
    """Get recent wallet transactions."""
    result = await db.execute(
        select(WalletTransaction)
        .where(WalletTransaction.user_id == user_id)
        .order_by(desc(WalletTransaction.created_at))
        .limit(limit)
    )
    return list(result.scalars().all())


async def get_inventory(db: AsyncSession, user_id: UUID) -> dict[str, int]:
    """Get user inventory as {item_type: quantity}."""
    result = await db.execute(
        select(RewardsInventory).where(RewardsInventory.user_id == user_id)
    )
    return {r.item_type: r.quantity for r in result.scalars().all()}


async def get_item_quantity(db: AsyncSession, user_id: UUID, item_type: str) -> int:
    """Get quantity of a specific item."""
    result = await db.execute(
        select(RewardsInventory).where(
            and_(RewardsInventory.user_id == user_id, RewardsInventory.item_type == item_type)
        )
    )
    inv = result.scalar_one_or_none()
    return inv.quantity if inv else 0


async def add_item(db: AsyncSession, user_id: UUID, item_type: str, quantity: int = 1) -> int:
    """Add item(s) to inventory. Returns new quantity."""
    result = await db.execute(
        select(RewardsInventory).where(
            and_(RewardsInventory.user_id == user_id, RewardsInventory.item_type == item_type)
        )
    )
    inv = result.scalar_one_or_none()
    if inv is None:
        inv = RewardsInventory(user_id=user_id, item_type=item_type, quantity=quantity)
        db.add(inv)
    else:
        inv.quantity += quantity
    await db.flush()
    return inv.quantity


async def use_item(db: AsyncSession, user_id: UUID, item_type: str) -> bool:
    """Use one item from inventory. Returns True if successful."""
    result = await db.execute(
        select(RewardsInventory).where(
            and_(RewardsInventory.user_id == user_id, RewardsInventory.item_type == item_type)
        )
    )
    inv = result.scalar_one_or_none()
    if inv is None or inv.quantity <= 0:
        return False
    inv.quantity -= 1
    await db.flush()
    return True


async def buy_streak_freeze(db: AsyncSession, user_id: UUID) -> dict:
    """Buy a streak freeze token for STREAK_FREEZE_COST coins."""
    # Check balance
    result = await db.execute(
        select(UserProgress).where(UserProgress.user_id == user_id)
    )
    progress = result.scalar_one_or_none()
    if progress is None or progress.coins_balance < STREAK_FREEZE_COST:
        return {"ok": False, "error": "Yetarli coin yo'q", "balance": progress.coins_balance if progress else 0}

    # Deduct coins
    progress.coins_balance -= STREAK_FREEZE_COST

    # Log transaction
    await log_transaction(db, user_id, -STREAK_FREEZE_COST, "spend", "shop_purchase", "Streak freeze token")

    # Add to inventory
    new_qty = await add_item(db, user_id, "streak_freeze", 1)

    await db.flush()

    return {
        "ok": True,
        "balance": progress.coins_balance,
        "freeze_tokens": new_qty,
    }
