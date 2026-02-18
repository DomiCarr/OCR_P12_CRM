# app/repositories/employee_repository.py
"""
This module specializes the BaseRepository for the Employee model.
It provides specific lookup methods necessary for authentication
and staff management.
"""

from typing import Optional
from sqlalchemy.orm import Session
from app.models.employee import Employee
from app.repositories.base_repository import BaseRepository


class EmployeeRepository(BaseRepository[Employee]):
    """
    Data access layer for Employee-specific operations.
    """

    def __init__(self, session: Session):
        super().__init__(session, Employee)

    def get_all_employees(self):
        """
        Fetch all employees using the base repository method.
        """
        return self.get_all()

    def get_by_email(self, email: str) -> Optional[Employee]:
        """
        Fetch an employee by their unique email address.
        Used for authentication.
        """
        return self.session.query(self.model).filter(
            self.model.email == email
        ).first()

    def get_by_employee_number(self, emp_number: str) -> Optional[Employee]:
        """
        Fetch an employee by their unique employee number.
        """
        return self.session.query(self.model).filter(
            self.model.employee_number == emp_number
        ).first()