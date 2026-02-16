# app/models/department.py
from typing import TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, pk_id, str_50

if TYPE_CHECKING:
    from app.models.employee import Employee


class Department(Base):
    """
    Represents a business unit (MANAGEMENT, SALES, or SUPPORT).
    """

    __tablename__ = "department"

    id: Mapped[pk_id]
    name: Mapped[str_50] = mapped_column(unique=True)

    # Relationships
    employees: Mapped[list["Employee"]] = relationship(
        back_populates="department"
    )

    def __repr__(self) -> str:
        return f"<Department(name={self.name})>"