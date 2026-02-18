# app/utils/decorators.py
from functools import wraps
from typing import Callable, Any
from app.utils.token_storage import get_token
from app.utils.jwt_handler import decode_token


def require_auth(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(self, *args, **kwargs) -> Any:
        print(f"\n[DEBUG] Entering decorator for: {func.__name__}")

        # 1. Vérification des arguments passés
        user_data = kwargs.get("user_data")
        if user_data:
            print(f"[DEBUG] user_data found in kwargs: {user_data.get('email')}")
        else:
            print("[DEBUG] No user_data in kwargs, checking token storage...")

            # 2. Vérification du token sur le disque
            token = get_token()
            if not token:
                print("[DEBUG] No token found in storage.")
            else:
                print(f"[DEBUG] Token found (starts with: {token[:10]}...)")
                user_data = decode_token(token)
                if user_data:
                    print(f"[DEBUG] Token decoded successfully: {user_data.get('email')}")
                else:
                    print("[DEBUG] Token decoding failed (expired or invalid).")

        if not user_data:
            print("[DEBUG] Auth failed: returning empty list.")
            return []

        # 3. Injection forcée dans kwargs pour le contrôleur
        kwargs["user_data"] = user_data
        print(f"[DEBUG] Executing {func.__name__} with user_data.")
        return func(self, *args, **kwargs)

    return wrapper