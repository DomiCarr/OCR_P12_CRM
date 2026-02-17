# app/utils/jwt_handler.py
"""
This module handles JSON Web Token (JWT) generation and validation.
It ensures that user sessions are persistent, secure, and include
expiration logic as required by the technical specifications.
"""

import os
import datetime
from typing import Optional
import jwt


# Configuration from environment variables
SECRET_KEY = os.getenv("JWT_SECRET", "default-secret-key-to-change")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
TOKEN_EXPIRATION_HOURS = 12


def create_token(employee_id: int, department_name: str) -> str:
    """
    Generate a JWT token containing employee ID and department.
    The token is set to expire in 12 hours.
    """
    payload = {
        "sub": employee_id,
        "department": department_name,
        "iat": datetime.datetime.utcnow(),
        "exp": (
            datetime.datetime.utcnow() +
            datetime.timedelta(hours=TOKEN_EXPIRATION_HOURS)
        )
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> Optional[dict]:
    """
    Decode and validate a JWT token.
    Returns the payload if valid, or None if expired/invalid.
    """
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None