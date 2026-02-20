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
                f"From: {event.event_date_start} To: {event.event_date_end} | "
                f"Support: {support}"
            )

    def ask_event_details(self) -> dict:
        """Prompt user for new event information."""
        print("\n=== Add New Event ===")
        return {
            "name": self.ask_input("Event Name"),
            "event_date_start": self.ask_input(
                "Event Start (YYYY-MM-DD HH:MM:SS)"
            ),
            "event_date_end": self.ask_input(
                "Event End (YYYY-MM-DD HH:MM:SS)"
            ),
            "location": self.ask_input("Location"),
            "attendees": self.ask_input("Attendees"),
            "notes": self.ask_input("Notes"),
        }

    def ask_event_update_details(self) -> dict:
        """Prompt user for event update information."""
        print("\n=== Update Event ===")
        return {
            "event_date_start": self.ask_input(
                "Event Start (YYYY-MM-DD HH:MM:SS) [Leave empty to skip]"
            ),
            "event_date_end": self.ask_input(
                "Event End (YYYY-MM-DD HH:MM:SS) [Leave empty to skip]"
            ),
            "location": self.ask_input("Location [Leave empty to skip]"),
            "attendees": self.ask_input("Attendees [Leave empty to skip]"),
            "notes": self.ask_input("Notes [Leave empty to skip]"),
            "support_contact_id": self.ask_input(
                "Support Contact ID [Leave empty to skip]"
            ),
        }