# app/controllers/employee_controller.py
"""
Controller handling business logic for Employee management.
"""

import sentry_sdk

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
        Sentry audit:
        - Logs each successful employee creation as an informational event.
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

        # Audit log only on success
        if created_employee:
            sentry_sdk.set_tag("audit", "employee")
            sentry_sdk.capture_message("employee.created", level="info")
            sentry_sdk.set_context(
                "employee_action",
                {
                    "action": "created",
                    "actor_id": user_data.get("id"),
                    "target_employee_id": created_employee.id,
                    "department_id": getattr(created_employee, "department_id", None),
                },
            )

        return created_employee

    @require_auth
    def update_employee(self, user_data: dict, emp_id: int, update_data: dict):
        """
        Update an existing employee's data.

        Sentry audit:
        - Logs each successful employee update as an informational event.
        - Records which fields were updated (excluding password).
        """
        self.auth_controller.current_user_data = user_data

        if not self.auth_controller.check_user_permission("update_employee"):
            return None

        # Capture updated fields BEFORE mutating update_data
        updated_fields = sorted(list(update_data.keys()))

        if "password" in update_data:
            update_data["password"] = hash_password(update_data["password"])

        updated_emp = self.repository.update(emp_id, update_data)

        # Audit log only on success
        if updated_emp:
            safe_fields = [f for f in updated_fields if f != "password"]

            sentry_sdk.set_tag("audit", "employee")
            sentry_sdk.capture_message("employee.updated", level="info")
            sentry_sdk.set_context(
                "employee_action",
                {
                    "action": "updated",
                    "actor_id": user_data.get("id"),
                    "target_employee_id": emp_id,
                    "updated_fields": safe_fields,
                },
            )
        return updated_emp