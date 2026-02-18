# app/views/client_view.py
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
                f"Email: {client.email} | Company: {client.company_name}"
            )

    def ask_client_details(self) -> dict:
        """Prompt user for new client information."""
        print("\n=== Add New Client ===")
        return {
            "full_name": self.ask_input("Full Name"),
            "email": self.ask_input("Email"),
            "phone": self.ask_input("Phone"),
            "company_name": self.ask_input("Company Name")
        }