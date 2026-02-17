# app/controllers/auth_controller.py
"""
This module handles the authentication logic, integrating JWT generation
and local storage to provide persistent user sessions.
"""

from typing import Optional
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

    def login(self, email: str, password: str) -> bool:
        """
        Authenticate user and save a JWT locally if successful.
        """
        employee = self.repository.get_by_email(email)

        if employee and verify_password(employee.password, password):
            # Generate and save token locally
            token = create_token(employee.id, employee.department.name)
            save_token(token)
            return True

        return False

    def logout(self) -> None:
        """
        Clear the session by deleting the local token.
        """
        delete_token()
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
            self.current_user_data = payload
            return payload

        # Token expired or invalid
        delete_token()
        return None

    def check_user_permission(self, action: str) -> bool:
        """
        Check permission based on the department stored in the JWT.
        """
        user = self.get_logged_in_user()
        if not user:
            return False

        return has_permission(action, user["department"])