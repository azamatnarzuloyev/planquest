from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import (
    create_access_token,
    parse_init_data_user,
    verify_telegram_init_data,
)
from app.schemas.auth import AuthRequest, AuthResponse
from app.schemas.user import UserResponse
from app.services.user_service import get_or_create_user

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/telegram", response_model=AuthResponse)
async def auth_telegram(
    body: AuthRequest,
    db: AsyncSession = Depends(get_db),
) -> AuthResponse:
    """
    Authenticate via Telegram Mini App initData.
    Verifies the initData signature, creates user if needed, returns JWT.
    """
    # 1. Verify initData
    verified_data = verify_telegram_init_data(body.init_data)
    if verified_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired Telegram initData",
        )

    # 2. Parse user info
    user_info = parse_init_data_user(verified_data)
    if user_info is None or not user_info.get("telegram_id"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not extract user from initData",
        )

    # 3. Get or create user
    user, is_new = await get_or_create_user(
        db=db,
        telegram_id=user_info["telegram_id"],
        first_name=user_info["first_name"],
        last_name=user_info.get("last_name"),
        username=user_info.get("username"),
    )

    # 4. Create JWT
    access_token = create_access_token(
        user_id=str(user.id),
        telegram_id=user.telegram_id,
    )

    return AuthResponse(
        access_token=access_token,
        user=UserResponse.model_validate(user),
    )
