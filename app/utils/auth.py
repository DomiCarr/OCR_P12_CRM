# app/utils/auth.py
"""
This module handles secure password management using the Argon2 hashing
algorithm. It provides utilities for hashing plain text passwords and
verifying them against stored hashes.
"""

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, InvalidHashError

# Initialize the hasher with default secure parameters
ph = PasswordHasher()


def hash_password(password: str) -> str:
    """
    Hash a password using Argon2.
    """
    return ph.hash(password)


def verify_password(hashed_password: str, plain_password: str) -> bool:
    """
    Verify a password against its Argon2 hash.
    """
    try:
        return ph.verify(hashed_password, plain_password)
    except (VerifyMismatchError, InvalidHashError):
        return False