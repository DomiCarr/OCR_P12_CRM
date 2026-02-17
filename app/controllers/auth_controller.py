# app/controllers/auth_controller.py
"""
This module contains the AuthController class, which orchestrates
the authentication flow by linking the EmployeeRepository,
the password utility, and the permission system.
"""

from typing import Optional
from app.models.employee import Employee
from app.repositories.employee_repository import EmployeeRepository
from app.utils.auth import verify_password
from app.utils.permissions import has_permission


class AuthController:
    """
    Handles authentication-related logic, including login validation
    and session-level permission checks.
    """

    def __init__(self, employee_repository: EmployeeRepository):
        self.repository = employee_repository
        self.current_user: Optional[Employee] = None

    def login(self, email: str, password: str) -> bool:
        """
        Validate credentials and set the current user if successful.
        """
        employee = self.repository.get_by_email(email)

        if employee and verify_password(employee.password, password):
            self.current_user = employee
            return True

        return False

    def logout(self) -> None:
        """
        Clear the current authenticated user session.
        """
        self.current_user = None

    def check_user_permission(self, action: str) -> bool:
        """
        Verify if the logged-in user has permission for a specific action.
        """
        if not self.current_user:
            return False

        return has_permission(
            action,
            self.current_user.department.name
        )