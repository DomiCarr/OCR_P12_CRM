# app/models/employee.py
"""
This module defines the Employee model, which stores staff member information,
credentials, and their association with departments and managed entities
such as clients and events.
"""

from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, pk_id, str_50, str_100, str_255, str_20

if TYPE_CHECKING:
    from app.models.department import Department
    from app.models.client import Client
    from app.models.event import Event


class Employee(Base):
    """
    Represents a staff member of Epic Events.
    """

    __tablename__ = "employee"

    id: Mapped[pk_id]
    full_name: Mapped[str_50]
    email: Mapped[str_100] = mapped_column(unique=True)
    password: Mapped[str_255]
    employee_number: Mapped[str_20] = mapped_column(unique=True)

    # Foreign Key to Department
    department_id: Mapped[int] = mapped_column(ForeignKey("department.id"))

    # Relationships
    department: Mapped["Department"] = relationship(back_populates="employees")

    # Managed entities (Sales/Support roles)
    managed_clients: Mapped[list["Client"]] = relationship(
        back_populates="sales_contact"
    )
    assigned_events: Mapped[list["Event"]] = relationship(
        back_populates="support_contact"
    )

    def __repr__(self) -> str:
        return (
            f"<Employee(name={self.full_name}, "
            f"department_id={self.department_id})>"
        )