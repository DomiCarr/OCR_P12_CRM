# app/views/contract_view.py
"""
View for Contract related interactions.
"""
from app.views.base_view import BaseView


class ContractView(BaseView):
    """Handles contract display and inputs."""

    def display_contracts(self, contracts: list):
        """Print the list of all contracts."""
        print("\n=== Contracts List ===")
        if not contracts:
            print("No contracts found.")
            return
        for contract in contracts:
            status = "Signed" if contract.is_signed else "Not Signed"
            print(
                f"ID: {contract.id} | Client: {contract.client.full_name} | "
                f"Total Amount: {contract.total_amount} | Status: {status}"
            )