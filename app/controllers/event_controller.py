# app/controllers/event_controller.py
"""
Controller handling business logic for Event management.
"""

from app.models.event import Event
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
        self.auth_controller.current_user_data = user_data
        if self.auth_controller.check_user_permission("read_event"):
            return self.repository.get_all_events()
        return None

    @require_auth
    def create_event(self, user_data: dict, event_data: dict, contract):
        """
        Create a new event if the contract is signed and user is the owner.
        """
        self.auth_controller.current_user_data = user_data
        if not self.auth_controller.check_user_permission("create_event"):
            print("Access denied: No permission to create events.")
            return None

        if contract.sales_contact_id != user_data["id"]:
            print("Access denied: You are not the sales contact for this client.")
            return None

        if not contract.is_signed:
            print("Access denied: Cannot create an event for an unsigned contract.")
            return None

        new_event = Event(**event_data)
        created_event = self.repository.add(new_event)

        if created_event:
            print(f"Event '{created_event.name}' created successfully.")
        return created_event

    @require_auth
    def update_event(self, user_data: dict, event_id: int, updates: dict):
        """Update event details if user is assigned support or management."""
        self.auth_controller.current_user_data = user_data
        if not self.auth_controller.check_user_permission("update_event"):
            print("Access denied: No update permission for events.")
            return None

        event = self.repository.get_by_id(event_id)
        if not event:
            print("Event not found.")
            return None

        # Logic: Support assigned or Management can update
        is_assigned = event.support_contact_id == user_data["id"]
        is_management = user_data["department"] == "MANAGEMENT"

        if not (is_assigned or is_management):
            print("Access denied: You are not the assigned support contact.")
            return None

        updated_event = self.repository.update(event_id, updates)
        if updated_event:
            print(f"Event '{updated_event.name}' updated.")
        return updated_event