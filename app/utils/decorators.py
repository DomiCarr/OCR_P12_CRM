# app/utils/decorators.py
"""
Authentication decorators for controller methods.
Ensures user_data is available via token or arguments.
"""

from functools import wraps
from typing import Any, Callable

import sentry_sdk

from app.utils.jwt_handler import decode_token
from app.utils.token_storage import get_token


# Handles dynamic `user_data` injection from kwargs, args, controller state, or token.
def require_auth(func: Callable) -> Callable:
    """
    Decorator that ensures a user is authenticated before executing a method.
    Injects user_data into kwargs to avoid shifting positional arguments.
    """

    def is_user_data(value: Any) -> bool:
        if not isinstance(value, dict):
            return False
        return "id" in value and "department" in value

    @wraps(func)
    def wrapper(self, *args, **kwargs) -> Any:
        sentry_sdk.add_breadcrumb(
            category="auth",
            message=f"Checking authentication for {func.__name__}",
            level="info",
        )

        user_data = kwargs.get("user_data")

        if not user_data and args and is_user_data(args[0]):
            user_data = args[0]

        if not user_data and hasattr(self, "auth_controller"):
            auth_ctrl = getattr(self, "auth_controller")
            current = getattr(auth_ctrl, "current_user_data", None)
            if current:
                user_data = current

        if not user_data:
            token = get_token()
            if token:
                user_data = decode_token(token)

        if not user_data:
            sentry_sdk.add_breadcrumb(
                category="auth",
                message="Authentication failed: No user data found",
                level="warning",
            )
            return None

        if "user_data" in kwargs:
            return func(self, *args, **kwargs)

        if args and is_user_data(args[0]):
            return func(self, *args, **kwargs)

        try:
            return func(self, *args, user_data=user_data, **kwargs)
        except TypeError:
            return func(self, user_data, *args, **kwargs)

    return wrapper
