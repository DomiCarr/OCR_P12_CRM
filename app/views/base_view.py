# app/views/base_view.py
"""
Base class for all views in the application.
Provides common display methods for CLI interaction.
"""


class BaseView:
    """Provides common display methods for CLI interaction."""

    def display_message(self, message: str):
        """Display a simple text message."""
        print(f"\n{message}")

    def display_error(self, message: str):
        """Display an error message formatted for visibility."""
        print(f"\n[ERROR] {message}")

    def ask_input(self, prompt: str) -> str:
        """Helper to get user input."""
        return input(f"{prompt}: ").strip()