# app/repositories/event_repository.py
"""
Data access layer for Event-specific operations.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.event import Event
from app.repositories.base_repository import BaseRepository


class EventRepository(BaseRepository[Event]):
    """
    Repository handling Event database queries.
    """

    def __init__(self, session: Session):
        super().__init__(session, Event)

    def get_all_events(self) -> List[Event]:
        """
        Fetch all events by calling the inherited get_all method.
        """
        return self.get_all()

    def get_events_without_support(self) -> List[Event]:
        """
        Fetch all events that have no support contact assigned.
        """
        return self.session.query(self.model).filter(
            self.model.support_contact_id == None  # noqa: E711
        ).all()

    def get_my_events(self, support_id: int) -> List[Event]:
        """
        Fetch events assigned to a specific support employee.
        """
        return self.session.query(self.model).filter(
            self.model.support_contact_id == support_id
        ).all()