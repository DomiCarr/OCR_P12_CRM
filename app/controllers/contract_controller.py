# app/controllers/contract_controller.py
"""
Controller handling business logic for Contract management.
"""

from app.repositories.contract_repository import ContractRepository
from app.utils.decorators import require_auth


class ContractController:
    """Manages contract-related operations."""

    def __init__(self, repository: ContractRepository, auth_controller):
        self.repository = repository
        self.auth_controller = auth_controller

    @require_auth
    def list_all_contracts(self, user_data: dict):
        """
        Fetch all contracts if allowed.
        """
        self.auth_controller.current_user_data = user_data
        if self.auth_controller.check_user_permission("read_contract"):
            return self.repository.get_all_contracts()
        return None