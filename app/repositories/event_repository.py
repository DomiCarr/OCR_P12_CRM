# app/repositories/event_repository.py
"""
Data access layer for Event-specific operations.
"""

from sqlalchemy.orm import Session
from app.models.event import Event
from app.repositories.base_repository import BaseRepository


class EventRepository(BaseRepository[Event]):
    """
    Repository handling Event database queries.
    """

    def __init__(self, session: Session):
        super().__init__(session, Event)

    def get_all_events(self):
        """
        Fetch all events using the base repository method.
        """
        return self.get_all()