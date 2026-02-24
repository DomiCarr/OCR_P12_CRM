# app/controllers/contract_controller.py
"""
Controller handling business logic for Contract management.
"""

from app.models.client import Client
from app.models.contract import Contract
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

    @require_auth
    def list_unsigned_contracts(self, user_data: dict):
        """List unsigned contracts, optionally filtered for sales ownership."""
        self.auth_controller.current_user_data = user_data
        if not self.auth_controller.check_user_permission("read_contract"):
            return None

        contracts = self.repository.get_unsigned_contracts()
        if user_data.get("department") == "SALES":
            return [
                c for c in contracts
                if c.sales_contact_id == user_data.get("id")
            ]
        return contracts

    @require_auth
    def list_unpaid_contracts(self, user_data: dict):
        """List unpaid contracts, optionally filtered for sales ownership."""
        self.auth_controller.current_user_data = user_data
        if not self.auth_controller.check_user_permission("read_contract"):
            return None

        contracts = self.repository.get_unpaid_contracts()
        if user_data.get("department") == "SALES":
            return [
                c for c in contracts
                if c.sales_contact_id == user_data.get("id")
            ]
        return contracts

    @require_auth
    def create_contract(self, user_data: dict, contract_data: dict):
        """Create a new contract for a client."""
        self.auth_controller.current_user_data = user_data
        if self.auth_controller.check_user_permission("create_contract"):
            if "sales_contact_id" not in contract_data:
                client_id = contract_data.get("client_id")
                if client_id is None:
                    print("Client ID is required to create a contract.")
                    return None

                client = (
                    self.repository.session.query(Client)
                    .filter_by(id=client_id)
                    .first()
                )
                if not client:
                    print("Client not found.")
                    return None

                contract_data["sales_contact_id"] = client.sales_contact_id

            new_contract = Contract(**contract_data)
            created_contract = self.repository.add(new_contract)

            if created_contract:
                print(f"Contract {created_contract.id} created successfully.")
            return created_contract

        print("Access denied: You do not have permission to create a contract.")
        return None

    @require_auth
    def update_contract(self, user_data: dict, contract_id: int, updates: dict):
        """Update contract details if user has permission."""
        self.auth_controller.current_user_data = user_data
        if not self.auth_controller.check_user_permission("update_contract"):
            print("Access denied: No update permission for contracts.")
            return None

        contract = self.repository.get_by_id(contract_id)
        if not contract:
            print("Contract not found.")
            return None

        # Logic: Sales can only update their own contracts. Management can
        # update all.
        is_owner = contract.sales_contact_id == user_data["id"]
        is_management = user_data["department"] == "MANAGEMENT"

        if not (is_owner or is_management):
            print("Access denied: You are not the assigned sales contact.")
            return None

        updated_contract = self.repository.update(contract_id, updates)
        if updated_contract:
            print(f"Contract {updated_contract.id} updated.")
        return updated_contract