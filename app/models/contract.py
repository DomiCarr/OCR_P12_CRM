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


class Contract(Base):
    """
    Represents a financial agreement with a client.
    """

    __tablename__ = "contract"

    id: Mapped[pk_id]
    total_amount: Mapped[float] = mapped_column(Numeric(10, 2))
    remaining_amount: Mapped[float] = mapped_column(Numeric(10, 2))
    status: Mapped[bool] = mapped_column(Boolean, default=False)

    # Audit timestamps
    created_at: Mapped[timestamp_now]
    last_update: Mapped[timestamp_update]

    # Foreign Keys
    client_id: Mapped[int] = mapped_column(ForeignKey("client.id"))

    # Relationships
    client: Mapped["Client"] = relationship(back_populates="contracts")
    event: Mapped["Event"] = relationship(back_populates="contract")

    def __repr__(self) -> str:
        return (
            f"<Contract(id={self.id}, "
            f"remaining={self.remaining_amount}, "
            f"signed={self.status})>"
        )