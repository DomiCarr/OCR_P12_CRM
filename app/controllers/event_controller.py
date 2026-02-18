# app/controllers/event_controller.py
"""
Controller handling business logic for Event management.
"""

from app.repositories.event_repository import EventRepository
from app.utils.decorators import require_auth


class EventController:
    """Manages event-related operations."""

    def __init__(self, repository: EventRepository, auth_controller):
        self.repository = repository
        self.auth_controller = auth_controller

    @require_auth
    def list_all_events(self, user_data: dict):
        """
        Fetch all events if allowed.
        """
        if self.auth_controller.check_user_permission("read_event"):
            return self.repository.get_all_events()
        return None