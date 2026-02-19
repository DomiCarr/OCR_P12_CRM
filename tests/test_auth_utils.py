# tests/test_auth_utils.py
"""
Unit tests for authentication utilities.

Tests included:
- test_password_hashing: Verify Argon2 hashing and verification.
- test_password_verification_fail: Ensure incorrect passwords are rejected.
- test_token_lifecycle: Save, retrieve, and delete token from storage.
"""

import os
from app.utils.auth import hash_password, verify_password
from app.utils.token_storage import save_token, get_token, delete_token, TOKEN_FILE


def test_password_hashing():
    """Test that hashing and verification work correctly with Argon2."""
    raw_password = "secure_password_2026"
    hashed = hash_password(raw_password)

    assert hashed != raw_password
    assert verify_password(hashed, raw_password) is True


def test_password_verification_fail():
    """Test that verification fails with a wrong password."""
    hashed = hash_password("correct_one")
    assert verify_password("wrong_one", hashed) is False


def test_token_lifecycle():
    """Test the full lifecycle: saving, getting, and deleting a token."""
    # Ensure a clean state
    if os.path.exists(TOKEN_FILE):
        os.remove(TOKEN_FILE)

    test_token = "abc.123.jwt.token"

    # Save
    save_token(test_token)
    assert os.path.exists(TOKEN_FILE)

    # Get
    retrieved = get_token()
    assert retrieved == test_token

    # Delete
    delete_token()
    assert not os.path.exists(TOKEN_FILE)
    assert get_token() is None