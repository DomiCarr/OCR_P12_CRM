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
                f"Sales Contact: {contract.sales_contact.full_name} | "
                f"Total: {contract.total_amount} | Status: {status}"
            )

    def ask_contract_details(self) -> dict:
        """Prompt user for new contract information."""
        print("\n=== Add New Contract ===")
        return {
            "client_id": self.ask_input("Client ID"),
            "total_amount": self.ask_input("Total Amount"),
            "remaining_amount": self.ask_input("Remaining Amount"),
            "is_signed": self.ask_input("Is Signed (y/n) [Leave empty for n]"),
        }

    def ask_contract_update_details(self) -> dict:
        """Prompt user for contract update information."""
        print("\n=== Update Contract ===")
        return {
            "total_amount": self.ask_input("Total Amount [Leave empty to skip]"),
            "remaining_amount": self.ask_input(
                "Remaining Amount [Leave empty to skip]"
            ),
            "is_signed": self.ask_input("Is Signed (y/n) [Leave empty to skip]"),
        }