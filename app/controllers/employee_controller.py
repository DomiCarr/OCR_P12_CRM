# app/controllers/employee_controller.py
"""
Controller handling business logic for Employee management.
"""

from app.models.employee import Employee
from app.repositories.employee_repository import EmployeeRepository
from app.utils.decorators import require_auth
from app.utils.auth import hash_password


class EmployeeController:
    """Manages employee-related operations."""

    def __init__(self, repository: EmployeeRepository, auth_controller):
        self.repository = repository
        self.auth_controller = auth_controller

    @require_auth
    def list_all_employees(self, user_data: dict):
        """
        Fetch all employees if the user has the 'read_employee' permission.
        """
        self.auth_controller.current_user_data = user_data

        if self.auth_controller.check_user_permission("read_employee"):
            return self.repository.get_all()

        return []

    @require_auth
    def create_employee(self, user_data: dict, employee_data: dict):
        """
        Create a new employee after permission check and password hashing.
        """
        self.auth_controller.current_user_data = user_data

        if not self.auth_controller.check_user_permission("create_employee"):
            return None

        # Hash the password before storage
        employee_data["password"] = hash_password(employee_data["password"])

        # Create the instance
        new_employee = Employee(**employee_data)

        # Pass the instance (not the dict) to the repository
        created_employee = self.repository.add(new_employee)
        return created_employee

    @require_auth
    def update_employee(self, user_data: dict, emp_id: int, update_data: dict):
        """
        Update an existing employee's data.
        """
        self.auth_controller.current_user_data = user_data

        if not self.auth_controller.check_user_permission("update_employee"):
            return None

        if "password" in update_data:
            update_data["password"] = hash_password(update_data["password"])

        updated_emp = self.repository.update(emp_id, update_data)
        return updated_emp