"""Chest generation, loot tables, and opening logic."""

import json
import logging
import random
from datetime import datetime
from uuid import UUID

from sqlalchemy import and_, desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chest import Chest
from app.services.wallet_service import add_item, log_transaction
from app.services.xp_service import get_or_create_progress

logger = logging.getLogger(__name__)

# === Loot Tables ===
# Each table: list of (item, weight)
# item: {"type": "coins", "amount": N} or {"type": "freeze", "amount": 1} or {"type": "xp", "amount": N}

LOOT_TABLES = {
    "common": {  # daily mission chest
        "coins_range": (10, 30),
        "bonus_rolls": [
            ({"type": "freeze", "amount": 1}, 0.10),  # 10% chance
            ({"type": "xp", "amount": 25}, 0.20),      # 20% chance
        ],
    },
    "rare": {  # weekly mission / streak chest
        "coins_range": (30, 80),
        "bonus_rolls": [
            ({"type": "freeze", "amount": 1}, 0.25),   # 25% chance
            ({"type": "xp", "amount": 50}, 0.30),       # 30% chance
            ({"type": "freeze", "amount": 2}, 0.05),    # 5% chance
        ],
    },
    "epic": {  # level chest / big streak
        "coins_range": (50, 150),
        "bonus_rolls": [
            ({"type": "freeze", "amount": 1}, 0.40),   # 40% chance
            ({"type": "xp", "amount": 100}, 0.30),      # 30% chance
            ({"type": "freeze", "amount": 3}, 0.10),    # 10% chance
        ],
    },
}

CHEST_TYPE_RARITY = {
    "daily_mission": "common",
    "weekly_mission": "rare",
    "streak": "rare",
    "level": "epic",
}


def _roll_loot(rarity: str) -> list[dict]:
    """Roll loot from the loot table."""
    table = LOOT_TABLES.get(rarity, LOOT_TABLES["common"])
    loot = []

    # Guaranteed coins
    coins = random.randint(*table["coins_range"])
    loot.append({"type": "coins", "amount": coins})

    # Bonus rolls
    for item, chance in table["bonus_rolls"]:
        if random.random() < chance:
            loot.append(item)

    return loot


async def create_chest(
    db: AsyncSession,
    user_id: UUID,
    chest_type: str,
    source: str = "",
) -> Chest:
    """Create a new unopened chest."""
    rarity = CHEST_TYPE_RARITY.get(chest_type, "common")
    chest = Chest(
        user_id=user_id,
        type=chest_type,
        rarity=rarity,
        status="unopened",
        source=source,
    )
    db.add(chest)
    await db.flush()
    logger.info(f"Chest created: type={chest_type} rarity={rarity} user={user_id}")
    return chest


async def get_unopened_chests(db: AsyncSession, user_id: UUID) -> list[Chest]:
    """Get all unopened chests for a user."""
    result = await db.execute(
        select(Chest)
        .where(and_(Chest.user_id == user_id, Chest.status == "unopened"))
        .order_by(desc(Chest.created_at))
    )
    return list(result.scalars().all())


async def get_chest_by_id(db: AsyncSession, chest_id: UUID, user_id: UUID) -> Chest | None:
    """Get a specific chest owned by user."""
    result = await db.execute(
        select(Chest).where(and_(Chest.id == chest_id, Chest.user_id == user_id))
    )
    return result.scalar_one_or_none()


async def open_chest(db: AsyncSession, chest: Chest) -> dict:
    """Open a chest: roll loot, apply rewards, return loot data."""
    if chest.status == "opened":
        return json.loads(chest.loot_data)

    # Roll loot
    loot = _roll_loot(chest.rarity)

    # Apply rewards
    total_coins = 0
    total_xp = 0
    freeze_tokens = 0

    for item in loot:
        if item["type"] == "coins":
            total_coins += item["amount"]
        elif item["type"] == "xp":
            total_xp += item["amount"]
        elif item["type"] == "freeze":
            freeze_tokens += item["amount"]

    # Apply coins
    if total_coins > 0:
        progress = await get_or_create_progress(db, chest.user_id)
        progress.coins_balance += total_coins
        await log_transaction(db, chest.user_id, total_coins, "earn", "chest", f"Chest: {chest.type}")

    # Apply XP
    if total_xp > 0:
        from app.services.xp_service import award_xp
        await award_xp(db, chest.user_id, "chest", chest.id, total_xp)

    # Apply freeze tokens
    if freeze_tokens > 0:
        await add_item(db, chest.user_id, "streak_freeze", freeze_tokens)

    # Update chest
    loot_data = {"items": loot, "total_coins": total_coins, "total_xp": total_xp, "freeze_tokens": freeze_tokens}
    chest.status = "opened"
    chest.loot_data = json.dumps(loot_data)
    chest.opened_at = datetime.utcnow()
    await db.flush()

    logger.info(f"Chest opened: id={chest.id} coins={total_coins} xp={total_xp} freeze={freeze_tokens}")
    return loot_data
