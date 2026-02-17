# app/utils/decorators.py
"""
This module provides decorators to enforce authentication and authorization
checks on controller methods or CLI commands.
"""

from functools import wraps
from typing import Callable, Any
from app.utils.token_storage import get_token
from app.utils.jwt_handler import decode_token


def require_auth(func: Callable) -> Callable:
    """
    Decorator to ensure a user is authenticated before executing a command.
    It reads and validates the local JWT token.
    """
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        token = get_token()
        if not token:
            print("[Error] You must be logged in to perform this action.")
            return None

        user_data = decode_token(token)
        if not user_data:
            print("[Error] Session expired or invalid. Please login again.")
            return None

        # Pass user data as an argument to the decorated function
        return func(user_data=user_data, *args, **kwargs)

    return wrapper