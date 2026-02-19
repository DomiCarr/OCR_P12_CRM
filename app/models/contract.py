# app/models/contract.py
"""
This module defines the Contract model, which stores financial agreements
with clients, including amounts, payment status, and audit timestamps.
"""

from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, Boolean, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import (
    Base,
    pk_id,
    timestamp_now,
    timestamp_update
)

if TYPE_CHECKING:
    from app.models.client import Client
    from app.models.event import Event
    from app.models.employee import Employee


class Contract(Base):
    """
    Represents a financial agreement with a client.
    """

    __tablename__ = "contract"

    id: Mapped[pk_id]
    total_amount: Mapped[float] = mapped_column(Numeric(10, 2))
    remaining_amount: Mapped[float] = mapped_column(Numeric(10, 2))
    is_signed: Mapped[bool] = mapped_column(Boolean, default=False)

    # Audit timestamps
    creation_date: Mapped[timestamp_now]
    last_update: Mapped[timestamp_update]

    # Foreign Keys
    client_id: Mapped[int] = mapped_column(ForeignKey("client.id"))
    sales_contact_id: Mapped[int] = mapped_column(ForeignKey("employee.id"))

    # Relationships
    client: Mapped["Client"] = relationship(back_populates="contracts")
    sales_contact: Mapped["Employee"] = relationship(
        back_populates="managed_contracts"
    )
    event: Mapped["Event"] = relationship(back_populates="contract")

    def __repr__(self) -> str:
        return (
            f"<Contract(id={self.id}, "
            f"remaining={self.remaining_amount}, "
            f"signed={self.is_signed})>"
        )