# app/utils/decorators.py
"""
Authentication decorators for controller methods.
Ensures user_data is available via token or arguments.
"""

from functools import wraps
from typing import Callable, Any
import sentry_sdk
from app.utils.token_storage import get_token
from app.utils.jwt_handler import decode_token


def require_auth(func: Callable) -> Callable:
    """
    Decorator that ensures a user is authenticated before executing a method.
    Injects user_data into the function arguments.
    """
    @wraps(func)
    def wrapper(self, *args, **kwargs) -> Any:
        # Add a breadcrumb to track the authentication attempt in Sentry
        sentry_sdk.add_breadcrumb(
            category="auth",
            message=f"Checking authentication for {func.__name__}",
            level="info",
        )

        # 1. Check if user_data is already passed
        user_data = kwargs.get("user_data")

        # 2. If not, try to retrieve it from token storage
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
            return []

        # 3. Inject user_data for the controller logic
        kwargs["user_data"] = user_data
        return func(self, *args, **kwargs)

    return wrapper