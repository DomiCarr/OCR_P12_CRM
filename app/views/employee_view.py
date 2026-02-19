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
                f"ID: {emp.id} | Name: {emp.full_name} | "
                f"Email: {emp.email} | Dept: {dept_name}"
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