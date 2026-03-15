import hashlib
import hmac
import json
import time
from datetime import datetime, timedelta, timezone
from urllib.parse import parse_qs, unquote

import jwt

from app.config import settings

# === Telegram initData Verification ===

INIT_DATA_MAX_AGE_SECONDS = 86400  # 24 hours


def verify_telegram_init_data(init_data: str, bot_token: str | None = None) -> dict | None:
    """
    Verify Telegram Mini App initData using HMAC-SHA256.
    Returns parsed data dict if valid, None if invalid.

    Algorithm (official Telegram docs):
    1. Parse init_data query string
    2. Extract "hash" parameter
    3. Sort remaining params alphabetically
    4. Join with "\\n" → data_check_string
    5. HMAC-SHA256(key="WebAppData", msg=bot_token) → secret_key
    6. HMAC-SHA256(key=secret_key, msg=data_check_string) → calculated_hash
    7. Compare calculated_hash with hash
    8. Check auth_date is not too old
    """
    if not init_data:
        return None

    token = bot_token or settings.BOT_TOKEN
    if not token:
        return None

    try:
        parsed = parse_qs(init_data, keep_blank_values=True)
        # parse_qs returns lists, flatten to single values
        data = {k: v[0] for k, v in parsed.items()}
    except Exception:
        return None

    received_hash = data.pop("hash", None)
    if not received_hash:
        return None

    # Check auth_date
    auth_date_str = data.get("auth_date")
    if not auth_date_str:
        return None

    try:
        auth_date = int(auth_date_str)
        if time.time() - auth_date > INIT_DATA_MAX_AGE_SECONDS:
            return None
    except (ValueError, TypeError):
        return None

    # Build data_check_string: sort keys, join as "key=value\n"
    data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(data.items()))

    # Calculate secret key: HMAC-SHA256("WebAppData", bot_token)
    secret_key = hmac.new(
        key=b"WebAppData",
        msg=token.encode("utf-8"),
        digestmod=hashlib.sha256,
    ).digest()

    # Calculate hash: HMAC-SHA256(secret_key, data_check_string)
    calculated_hash = hmac.new(
        key=secret_key,
        msg=data_check_string.encode("utf-8"),
        digestmod=hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(calculated_hash, received_hash):
        return None

    return data


def parse_init_data_user(data: dict) -> dict | None:
    """
    Extract user info from verified initData.
    The "user" field is a JSON string inside the query param.
    """
    user_str = data.get("user")
    if not user_str:
        return None

    try:
        user_data = json.loads(unquote(user_str))
        return {
            "telegram_id": user_data.get("id"),
            "first_name": user_data.get("first_name", ""),
            "last_name": user_data.get("last_name"),
            "username": user_data.get("username"),
        }
    except (json.JSONDecodeError, AttributeError):
        return None


# === JWT Token Management ===

JWT_ALGORITHM = "HS256"
JWT_EXPIRE_DAYS = 7


def create_access_token(user_id: str, telegram_id: int) -> str:
    """Create a JWT access token."""
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user_id,
        "telegram_id": telegram_id,
        "iat": now,
        "exp": now + timedelta(days=JWT_EXPIRE_DAYS),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=JWT_ALGORITHM)


def verify_access_token(token: str) -> dict | None:
    """
    Verify and decode a JWT token.
    Returns payload dict if valid, None if invalid/expired.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
