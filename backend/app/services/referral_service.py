"""Referral tracking, activation, and rewards."""

import logging
from datetime import datetime, timedelta
from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.referral import Referral
from app.models.user import User
from app.services.xp_service import award_xp
from app.services.wallet_service import log_transaction

logger = logging.getLogger(__name__)

MAX_REFERRALS = 50

# Rewards
REFERRER_ACTIVATE_XP = 100
REFERRER_ACTIVATE_COINS = 50
REFERRED_ACTIVATE_COINS = 50
REFERRER_D7_XP = 50
REFERRER_D7_COINS = 25


async def create_referral(
    db: AsyncSession,
    referrer_code: str,
    referred_user_id: UUID,
) -> Referral | None:
    """Create referral record. Returns None if invalid."""
    # Find referrer by code
    result = await db.execute(
        select(User).where(User.referral_code == referrer_code)
    )
    referrer = result.scalar_one_or_none()
    if referrer is None:
        logger.warning(f"Invalid referral code: {referrer_code}")
        return None

    # Anti-abuse: self-referral
    if referrer.id == referred_user_id:
        logger.warning("Self-referral blocked")
        return None

    # Anti-abuse: already referred
    existing = await db.execute(
        select(Referral).where(Referral.referred_user_id == referred_user_id)
    )
    if existing.scalar_one_or_none():
        return None

    # Anti-abuse: max referrals
    count = await db.execute(
        select(func.count()).where(Referral.referrer_user_id == referrer.id)
    )
    if count.scalar_one() >= MAX_REFERRALS:
        logger.warning(f"Referral limit reached for {referrer.id}")
        return None

    referral = Referral(
        referrer_user_id=referrer.id,
        referred_user_id=referred_user_id,
        referral_code=referrer_code,
        status="pending",
    )
    db.add(referral)
    await db.flush()
    logger.info(f"Referral created: {referrer.id} → {referred_user_id}")
    return referral


async def activate_referral(db: AsyncSession, referred_user_id: UUID) -> bool:
    """Activate referral when referred user completes onboarding. Awards both sides."""
    result = await db.execute(
        select(Referral).where(
            and_(Referral.referred_user_id == referred_user_id, Referral.status == "pending")
        )
    )
    referral = result.scalar_one_or_none()
    if referral is None:
        return False

    referral.status = "activated"
    referral.activated_at = datetime.utcnow()

    # Reward referrer
    await award_xp(db, referral.referrer_user_id, "referral", referral.id, REFERRER_ACTIVATE_XP, coins=REFERRER_ACTIVATE_COINS)
    await log_transaction(db, referral.referrer_user_id, REFERRER_ACTIVATE_COINS, "earn", "referral", "Referral aktivatsiya")

    # Reward referred
    from app.services.xp_service import get_or_create_progress
    progress = await get_or_create_progress(db, referred_user_id)
    progress.coins_balance += REFERRED_ACTIVATE_COINS
    await log_transaction(db, referred_user_id, REFERRED_ACTIVATE_COINS, "earn", "referral", "Taklif bonus")

    await db.flush()
    logger.info(f"Referral activated: {referral.referrer_user_id} → {referred_user_id}")
    return True


async def check_d7_bonus(db: AsyncSession) -> int:
    """Check activated referrals where referred user has been active 7+ days. Award D7 bonus."""
    cutoff = datetime.utcnow() - timedelta(days=7)

    result = await db.execute(
        select(Referral).where(
            and_(Referral.status == "activated", Referral.activated_at <= cutoff)
        )
    )
    referrals = list(result.scalars().all())
    rewarded = 0

    for ref in referrals:
        # Check if referred user is still active (has streak)
        from app.models.streak import Streak
        streak_result = await db.execute(
            select(Streak).where(
                and_(Streak.user_id == ref.referred_user_id, Streak.type == "activity")
            )
        )
        streak = streak_result.scalar_one_or_none()

        if streak and streak.current_count >= 3:  # At least some activity
            await award_xp(db, ref.referrer_user_id, "referral_d7", ref.id, REFERRER_D7_XP, coins=REFERRER_D7_COINS)
            ref.status = "d7_rewarded"
            ref.d7_rewarded_at = datetime.utcnow()
            rewarded += 1

    if rewarded:
        await db.flush()
    return rewarded


async def get_referral_stats(db: AsyncSession, user_id: UUID) -> dict:
    """Get referral statistics for a user."""
    total = await db.execute(
        select(func.count()).where(Referral.referrer_user_id == user_id)
    )
    activated = await db.execute(
        select(func.count()).where(
            and_(Referral.referrer_user_id == user_id, Referral.status.in_(["activated", "d7_rewarded"]))
        )
    )

    # Get referral code
    user_result = await db.execute(select(User.referral_code).where(User.id == user_id))
    code = user_result.scalar_one_or_none() or ""

    return {
        "referral_code": code,
        "total_referred": total.scalar_one(),
        "activated": activated.scalar_one(),
        "max_referrals": MAX_REFERRALS,
    }
