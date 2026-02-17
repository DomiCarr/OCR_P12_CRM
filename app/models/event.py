# app/models/event.py
"""
This module defines the Event model, representing a scheduled event
linked to a client, a contract, and potentially a support employee.
"""

from typing import TYPE_CHECKING, Optional
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import (
    Base,
    pk_id,
    str_50,
    text_type,
    timestamp_now,
    timestamp_update
)

if TYPE_CHECKING:
    from app.models.client import Client
    from app.models.employee import Employee
    from app.models.contract import Contract


class Event(Base):
    """
    Represents a scheduled event for a specific client and contract.
    """

    __tablename__ = "event"

    id: Mapped[pk_id]
    name: Mapped[str_50]
    event_date: Mapped[timestamp_now]
    location: Mapped[str_50]
    attendees: Mapped[int]
    notes: Mapped[text_type]

    # Audit timestamps
    created_at: Mapped[timestamp_now]
    last_update: Mapped[timestamp_update]

    # Foreign Keys
    client_id: Mapped[int] = mapped_column(ForeignKey("client.id"))
    contract_id: Mapped[int] = mapped_column(ForeignKey("contract.id"))
    support_contact_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("employee.id"), nullable=True
    )

    # Relationships
    client: Mapped["Client"] = relationship(back_populates="events")
    contract: Mapped["Contract"] = relationship(back_populates="event")
    support_contact: Mapped["Employee"] = relationship(
        back_populates="assigned_events"
    )

    def __repr__(self) -> str:
        return f"<Event(name={self.name}, date={self.event_date})>"