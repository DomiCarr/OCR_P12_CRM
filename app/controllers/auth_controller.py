# app/controllers/auth_controller.py
"""
This module handles the authentication logic, integrating JWT generation
and local storage to provide persistent user sessions.
"""

from typing import Optional
import sentry_sdk
from app.repositories.employee_repository import EmployeeRepository
from app.utils.auth import verify_password
from app.utils.permissions import has_permission
from app.utils.jwt_handler import create_token, decode_token
from app.utils.token_storage import save_token, get_token, delete_token


class AuthController:
    """
    Controller managing login, logout, and persistent session validation.
    """

    def __init__(self, employee_repository: EmployeeRepository):
        self.repository = employee_repository
        self.current_user_data: Optional[dict] = None

    def login(self, email: str, password: str) -> Optional[dict]:
        """
        Authenticate user and save a JWT locally if successful.
        """
        employee = self.repository.get_by_email(email)

        if employee and verify_password(employee.password, password):
            # Generate and save token locally
            token = create_token(employee.id, employee.department.name)
            save_token(token)

            # Return user data for main.py session management
            user_data = {
                "id": employee.id,
                "full_name": employee.full_name,
                "department": employee.department.name
            }

            # Attach user identity to Sentry scope for error tracking
            sentry_sdk.set_user({
                "id": str(employee.id),
                "username": employee.full_name,
                "department": employee.department.name
            })

            self.current_user_data = user_data
            return user_data

        return None

    def logout(self) -> None:
        """
        Clear the session by deleting the local token.
        """
        delete_token()
        # Clear Sentry user context to avoid cross-user error reporting
        sentry_sdk.set_user(None)
        self.current_user_data = None

    def get_logged_in_user(self) -> Optional[dict]:
        """
        Validate the local token and return user data if still valid.
        """
        token = get_token()
        if not token:
            return None

        payload = decode_token(token)
        if payload:
            # Restore Sentry user identity for persistent sessions
            sentry_sdk.set_user({
                "id": str(payload.get("id")),
                "department": payload.get("department")
            })
            self.current_user_data = payload
            return payload

        # Token expired or invalid
        delete_token()
        return None

    def check_user_permission(self, action: str) -> bool:
        """
        Check if the currently logged-in user has permission for an action.
        """
        if not self.current_user_data:
            return False

        dept = self.current_user_data.get("department")
        return has_permission(action, dept)