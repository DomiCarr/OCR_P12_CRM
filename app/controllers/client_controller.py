# app/controllers/client_controller.py
"""
Controller handling business logic for Client management.
Ensures authentication and permission checks before data access.
"""

from datetime import datetime
from app.repositories.client_repository import ClientRepository
from app.utils.decorators import require_auth


class ClientController:
    """Manages client-related operations."""

    def __init__(self, repository: ClientRepository, auth_controller):
        self.repository = repository
        self.auth_controller = auth_controller

    @require_auth
    def list_all_clients(self, user_data: dict):
        """Fetch all clients if the user has the 'read_client' permission."""
        self.auth_controller.current_user_data = user_data
        permission = "read_client"
        if self.auth_controller.check_user_permission(permission):
            return self.repository.get_all_clients()
        return []

    @require_auth
    def create_client(self, user_data: dict, client_data: dict):
        """Create a new client and associate with the current sales person."""
        self.auth_controller.current_user_data = user_data
        if self.auth_controller.check_user_permission("create_client"):
            # Set sales_contact_id from the current logged-in user
            client_data["sales_contact_id"] = user_data["id"]

            # Set last_contact to now if not provided
            if not client_data.get("last_contact"):
                client_data["last_contact"] = datetime.now()

            new_client = self.repository.add_client(client_data)
            print(f"Client '{new_client.full_name}' created successfully.")
            return new_client
        print("Access denied: You do not have permission to create a client.")
        return None