# app/views/main_menu_view.py
"""
Main menu view for the CRM application.
Adapts displayed options based on user department.
"""

from app.views.base_view import BaseView


class MainMenuView(BaseView):
    """Controller view for the main menu."""

    def display_menu(self, department: str):
        """Print the main menu options according to department."""
        print(f"\n=== Epic Events CRM - {department} Menu ===")
        print("1. List all clients")
        print("2. List all contracts")
        print("3. List all events")

        if department == "MANAGEMENT":
            print("10. Manage employees (Admin)")
        elif department == "SALES":
            print("20. Create new client")
        elif department == "SUPPORT":
            print("30. Update my events")

        print("0. Logout and Exit")

    def ask_menu_option(self) -> str:
        """Ask the user for a menu option."""
        return input("\nSelect an option: ").strip()