# app/repositories/department_repository.py
"""
This module specializes the BaseRepository for the Department model.
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.department import Department
from app.repositories.base_repository import BaseRepository


class DepartmentRepository(BaseRepository[Department]):
    """
    Data access layer for Department-specific operations.
    """

    def __init__(self, session: Session):
        super().__init__(session, Department)

    def get_all_departments(self) -> List[Department]:
        """
        Fetch all departments using the base repository method.
        """
        return self.get_all()

    def get_by_name(self, name: str) -> Optional[Department]:
        """
        Fetch a department by its unique name.
        """
        return self.session.query(self.model).filter(
            self.model.name == name
        ).first()