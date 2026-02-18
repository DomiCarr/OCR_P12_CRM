# app/utils/token_storage.py
"""
This module manages the local persistence of the JWT token.
It provides functions to save, retrieve, and delete the token from
a local file to maintain user sessions across CLI executions.
"""

import os
from typing import Optional

TOKEN_FILE = ".token"


def save_token(token: str) -> None:
    """
    Save the JWT token to a local hidden file.
    """
    with open(TOKEN_FILE, "w", encoding="utf-8") as f:
        f.write(token)


def get_token() -> Optional[str]:
    """
    Retrieve the JWT token from the local file if it exists.
    """
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r", encoding="utf-8") as f:
            return f.read().strip()
    return None


def delete_token() -> None:
    """
    Remove the local token file to log out the user.
    """
    if os.path.exists(TOKEN_FILE):
        os.remove(TOKEN_FILE)