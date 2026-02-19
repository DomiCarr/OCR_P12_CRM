# tests/test_jwt_handler.py
"""
Unit tests for JWT handler.

Tests included:
- test_create_and_decode_valid_token: Verify generation and decoding.
- test_decode_invalid_token: Ensure invalid strings return None.
- test_expired_token: Verify expiration logic returns None.
"""

import datetime
import jwt
from app.utils.jwt_handler import create_token, decode_token, SECRET_KEY, ALGORITHM


def test_create_and_decode_valid_token():
    """Verify that a generated token can be correctly decoded."""
    token = create_token(1, "Management")
    decoded = decode_token(token)

    assert decoded is not None
    assert decoded["sub"] == "1"
    assert decoded["department"] == "Management"


def test_decode_invalid_token():
    """Ensure that an invalid token returns None."""
    assert decode_token("invalid.token.string") is None


def test_expired_token():
    """Verify that an expired token returns None."""
    now = datetime.datetime.now(datetime.UTC)
    payload = {
        "sub": "1",
        "department": "Sales",
        "exp": int((now - datetime.timedelta(seconds=1)).timestamp())
    }
    expired_token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    decoded = decode_token(expired_token)
    assert decoded is None