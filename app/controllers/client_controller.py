# app/controllers/client_controller.py
"""
Controller handling business logic for Client management.
Ensures authentication and permission checks before data access.
"""

from datetime import datetime
from app.models.client import Client
from app.repositories.client_repository import ClientRepository
from app.utils.decorators import require_auth


class ClientController:
    """Manages client-related operations."""

    def __init__(self, repository: ClientRepository, auth_controller):
        self.repository = repository
        self.auth_controller = auth_controller

    @require_auth
    def list_all_clients(self, *args, user_data: dict | None = None):
        """Fetch all clients if the user has the 'read_client' permission."""
        if user_data is None and args:
            if isinstance(args[0], dict) and "id" in args[0]:
                user_data = args[0]

        if user_data is None:
            return []

        self.auth_controller.current_user_data = user_data
        permission = "read_client"
        if self.auth_controller.check_user_permission(permission):
            return self.repository.get_all_clients()
        return []

    @require_auth
    def create_client(
        self,
        *args,
        user_data: dict | None = None,
        client_data: dict | None = None,
    ):
        """Create a new client and associate with the current sales person."""
        if client_data is None and args:
            first = args[0]
            if isinstance(first, dict) and "id" in first and "department" in first:
                user_data = first
                if len(args) > 1:
                    client_data = args[1]
            else:
                client_data = first

        if user_data is None:
            user_data = getattr(self.auth_controller, "current_user_data", None)

        if not user_data or not client_data:
            return None

        self.auth_controller.current_user_data = user_data
        if self.auth_controller.check_user_permission("create_client"):
            client_data["sales_contact_id"] = user_data["id"]

            if not client_data.get("last_contact"):
                client_data["last_contact"] = datetime.now()

            new_client = Client(**client_data)
            created_client = self.repository.add(new_client)

            if created_client:
                print(f"Client '{created_client.full_name}' created.")
            return created_client

        print("Access denied: You do not have permission to create a client.")
        return None

    @require_auth
    def update_client(self, user_data: dict, client_id: int, updates: dict):
        """Update client if user is assigned sales contact or management."""
        self.auth_controller.current_user_data = user_data
        if not self.auth_controller.check_user_permission("update_client"):
            print("Access denied: No update permission.")
            return None

        client = self.repository.get_by_id(client_id)
        if not client:
            print("Client not found.")
            return None

        # Logic: Sales can only update their own clients. Management can update all.
        is_owner = client.sales_contact_id == user_data["id"]
        is_management = user_data["department"] == "MANAGEMENT"

        if not (is_owner or is_management):
            print("Access denied: You are not the assigned sales contact.")
            return None

        # Update last_contact timestamp
        updates["last_contact"] = datetime.now()

        # FIXED: Pass 'updates' as a dict to match BaseRepository.update signature
        updated_client = self.repository.update(client_id, updates)
        if updated_client:
            print(f"Client '{updated_client.full_name}' updated.")
        return updated_client
