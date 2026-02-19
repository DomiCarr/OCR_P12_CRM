# app/views/event_view.py
"""
View for Event related interactions.
"""
from app.views.base_view import BaseView


class EventView(BaseView):
    """Handles event display and inputs."""

    def display_events(self, events: list):
        """Print the list of all events."""
        print("\n=== Events List ===")
        if not events:
            print("No events found.")
            return
        for event in events:
            support = (
                event.support_contact.full_name
                if event.support_contact
                else "TBD"
            )
            print(
                f"ID: {event.id} | Name: {event.name} | "
                f"Date: {event.event_date} | Support: {support}"
            )