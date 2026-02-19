# app/views/base_view.py
"""
Base class for all views in the application.
Provides common display methods and input validation for CLI interaction.
"""

import re
from datetime import datetime


class BaseView:
    """Provides common display methods and input validation for CLI."""

    def display_message(self, message: str):
        """Display a simple text message."""
        print(f"\n{message}")

    def display_error(self, message: str):
        """Display an error message formatted for visibility."""
        print(f"\n[ERROR] {message}")

    def ask_input(self, prompt: str) -> str:
        """Helper to get user input."""
        return input(f"{prompt}: ").strip()

    def validate_email(self, email: str) -> bool:
        """Check if the email format is valid."""
        pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        if re.match(pattern, email):
            return True
        self.display_error("Invalid email format (ex: name@domain.com).")
        return False

    def validate_amount(self, amount: str) -> bool:
        """Check if the amount is a positive number."""
        try:
            val = float(amount)
            if val >= 0:
                return True
            self.display_error("Amount must be a positive value.")
        except ValueError:
            self.display_error("Amount must be a numeric value.")
        return False

    def validate_date(self, date_str: str) -> bool:
        """Check if the date format is valid (DD-MM-YYYY)."""
        try:
            datetime.strptime(date_str, "%d-%m-%Y")
            return True
        except ValueError:
            self.display_error("Invalid date format. Please use DD-MM-YYYY.")
            return False