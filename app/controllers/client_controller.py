# app/controllers/client_controller.py
"""
Controller handling business logic for Client management.
Ensures authentication and permission checks before data access.
"""

from app.repositories.client_repository import ClientRepository
from app.utils.decorators import require_auth


class ClientController:
    """Manages client-related operations."""

    def __init__(self, repository: ClientRepository, auth_controller):
        self.repository = repository
        self.auth_controller = auth_controller

    @require_auth
    def list_all_clients(self, user_data: dict):
        """
        Fetch all clients if the user has the 'read' permission.
        """
        # DEBUG: On vérifie ce que contient user_data
        print(f"[DEBUG] user_data content: {user_data}")

        # On force la mise à jour de la session interne du controller si nécessaire
        self.auth_controller.current_user_data = user_data

        permission = "read_client"
        if self.auth_controller.check_user_permission(permission):
            return self.repository.get_all_clients()

        # Si ça échoue encore, on affiche pourquoi
        print(f"[DEBUG] Access denied: Role {user_data.get('department')} lacks {permission}")
        return []