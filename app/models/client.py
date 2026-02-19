# app/models/client.py
"""
This module defines the Client model, which stores customer information,
contact details, and handles relationships with sales employees,
contracts, and events.
"""

from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import (
    Base,
    pk_id,
    str_50,
    str_100,
    str_20,
    timestamp_now,
    timestamp_update
)

if TYPE_CHECKING:
    from app.models.employee import Employee
    from app.models.event import Event
    from app.models.contract import Contract


class Client(Base):
    """
    Represents a customer in the CRM system.
    """

    __tablename__ = "client"

    id: Mapped[pk_id]
    full_name: Mapped[str_50]
    email: Mapped[str_100] = mapped_column(unique=True)
    phone: Mapped[str_20]
    company_name: Mapped[str_50]

    # New field for last business contact
    last_contact: Mapped[timestamp_now]

    # Audit timestamps
    creation_date: Mapped[timestamp_now]
    last_update: Mapped[timestamp_update]

    # Foreign Key to the Sales Contact (Employee)
    sales_contact_id: Mapped[int] = mapped_column(
        ForeignKey("employee.id")
    )

    # Relationships
    sales_contact: Mapped["Employee"] = relationship(
        back_populates="managed_clients"
    )
    contracts: Mapped[list["Contract"]] = relationship(
        back_populates="client"
    )
    events: Mapped[list["Event"]] = relationship(
        back_populates="client"
    )

    def __repr__(self) -> str:
        return (
            f"<Client(name={self.full_name}, "
            f"company={self.company_name})>"
        )