import hashlib
import hmac
import json
import time
from urllib.parse import urlencode

import pytest

from app.config import settings
from app.core.security import (
    create_access_token,
    parse_init_data_user,
    verify_access_token,
    verify_telegram_init_data,
)


def _build_init_data(user_data: dict, bot_token: str | None = None) -> str:
    """Helper: build a valid signed initData string for testing."""
    token = bot_token or settings.BOT_TOKEN
    auth_date = str(int(time.time()))
    user_json = json.dumps(user_data, separators=(",", ":"))

    params = {
        "user": user_json,
        "auth_date": auth_date,
    }

    # Build data_check_string
    data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(params.items()))

    # Calculate hash
    secret_key = hmac.new(b"WebAppData", token.encode(), hashlib.sha256).digest()
    hash_value = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

    params["hash"] = hash_value
    return urlencode(params)


# === initData verification tests ===


def test_verify_valid_init_data():
    """Valid initData should return parsed data."""
    user_data = {"id": 12345, "first_name": "Test", "username": "testuser"}
    init_data = _build_init_data(user_data)
    result = verify_telegram_init_data(init_data)
    assert result is not None
    assert "user" in result
    assert "auth_date" in result


def test_verify_invalid_signature():
    """Tampered initData should return None."""
    user_data = {"id": 12345, "first_name": "Test"}
    init_data = _build_init_data(user_data)
    # Tamper with the data
    init_data = init_data.replace("Test", "Hacked")
    result = verify_telegram_init_data(init_data)
    assert result is None


def test_verify_expired_init_data():
    """initData older than 24h should return None."""
    token = settings.BOT_TOKEN
    old_auth_date = str(int(time.time()) - 90000)  # 25 hours ago
    user_json = json.dumps({"id": 12345, "first_name": "Test"}, separators=(",", ":"))

    params = {"user": user_json, "auth_date": old_auth_date}
    data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(params.items()))
    secret_key = hmac.new(b"WebAppData", token.encode(), hashlib.sha256).digest()
    hash_value = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
    params["hash"] = hash_value

    result = verify_telegram_init_data(urlencode(params))
    assert result is None


def test_verify_empty_init_data():
    """Empty initData should return None."""
    assert verify_telegram_init_data("") is None
    assert verify_telegram_init_data("invalid=data") is None


# === parse_init_data_user tests ===


def test_parse_user_from_init_data():
    """Should extract user info from verified data."""
    user_data = {"id": 99999, "first_name": "Azamat", "last_name": "Dev", "username": "azamat"}
    init_data = _build_init_data(user_data)
    verified = verify_telegram_init_data(init_data)
    assert verified is not None

    user_info = parse_init_data_user(verified)
    assert user_info is not None
    assert user_info["telegram_id"] == 99999
    assert user_info["first_name"] == "Azamat"
    assert user_info["last_name"] == "Dev"
    assert user_info["username"] == "azamat"


# === JWT tests ===


def test_jwt_create_and_verify():
    """Created JWT should be verifiable."""
    token = create_access_token(user_id="abc-123", telegram_id=12345)
    payload = verify_access_token(token)
    assert payload is not None
    assert payload["sub"] == "abc-123"
    assert payload["telegram_id"] == 12345


def test_jwt_invalid_token():
    """Invalid JWT should return None."""
    assert verify_access_token("invalid.token.here") is None
    assert verify_access_token("") is None


def test_jwt_wrong_secret():
    """JWT signed with different secret should fail."""
    import jwt as pyjwt

    token = pyjwt.encode(
        {"sub": "test", "telegram_id": 1},
        "wrong-secret",
        algorithm="HS256",
    )
    assert verify_access_token(token) is None
