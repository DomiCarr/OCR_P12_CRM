"""
View for Client related interactions.
"""
from app.views.base_view import BaseView


class ClientView(BaseView):
    """Handles client display and inputs."""

    def display_clients(self, clients: list):
        """Print the list of all clients."""
        print("\n=== Clients List ===")
        if not clients:
            print("No clients found.")
            return
        for client in clients:
            print(
                f"ID: {client.id} | Name: {client.full_name} | "
                f"Email: {client.email} | Company: {client.company_name} | "
                f"Last Contact: {client.last_contact}"
            )

    def ask_client_details(self) -> dict:
        """Prompt user for new client information."""
        print("\n=== Add New Client ===")
        return {
            "full_name": self.ask_input("Full Name"),
            "email": self.ask_input("Email"),
            "phone": self.ask_input("Phone"),
            "company_name": self.ask_input("Company Name"),
            "last_contact": self.ask_input(
                "Last Contact Date (YYYY-MM-DD HH:MM:SS) "
                "[Leave empty for now]"
            )
        }

    def ask_client_update_details(self) -> dict:
        """Prompt user for client update information."""
        print("\n=== Update Client ===")
        return {
            "full_name": self.ask_input("Full Name [Leave empty to skip]"),
            "email": self.ask_input("Email [Leave empty to skip]"),
            "phone": self.ask_input("Phone [Leave empty to skip]"),
            "company_name": self.ask_input("Company Name [Leave empty to skip]"),
            "last_contact": self.ask_input(
                "Last Contact Date (YYYY-MM-DD HH:MM:SS) "
                "[Leave empty to skip]"
            ),
        }