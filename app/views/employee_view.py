# app/views/employee_view.py
"""
View for Employee related interactions.
"""
from app.views.base_view import BaseView


class EmployeeView(BaseView):
    """Handles employee display and inputs."""

    def display_employees(self, employees: list):
        """Print the list of all employees."""
        print("\n=== Employees List ===")
        if not employees:
            print("No employees found.")
            return
        for emp in employees:
            dept_name = emp.department.name if emp.department else "N/A"
            print(
                f"ID: {emp.id} | No: {emp.employee_number} | "
                f"Name: {emp.full_name} | Email: {emp.email} | "
                f"Dept: {dept_name}"
            )

    def ask_employee_details(self) -> dict:
        """Prompt user for new employee information."""
        print("\n=== Add New Employee ===")

        full_name = self.ask_input("Full Name")

        while True:
            email = self.ask_input("Email")
            if self.validate_email(email):
                break

        password = self.ask_input("Password")
        employee_number = self.ask_input("Employee Number")
        department_id = self.ask_input(
            "Department ID (1: Sales, 2: Support, 3: Management)"
        )

        return {
            "full_name": full_name,
            "email": email,
            "password": password,
            "employee_number": employee_number,
            "department_id": int(department_id) if department_id.isdigit() else 0
        }

    def ask_update_details(self) -> dict:
        """Prompt user for employee updates (all fields optional)."""
        print("\n=== Update Employee (Leave blank to keep current value) ===")

        full_name = self.ask_input("New Full Name (optional)")
        email = self.ask_input("New Email (optional)")
        password = self.ask_input("New Password (optional)")
        dept_id = self.ask_input("New Dept ID (optional)")

        details = {}
        if full_name:
            details["full_name"] = full_name
        if email:
            details["email"] = email
        if password:
            details["password"] = password
        if dept_id:
            details["department_id"] = int(dept_id) if dept_id.isdigit() else 0

        return details