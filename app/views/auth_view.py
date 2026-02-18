# app/views/auth_view.py
"""
View for authentication related interactions.
Handles login inputs and success/failure messages.
"""

from app.views.base_view import BaseView


class AuthView(BaseView):
    """Handles login inputs."""

    def ask_login_details(self) -> tuple[str, str]:
        """Prompt user for email and password."""
        print("\n=== Epic Events CRM - Login ===")
        email = self.ask_input("Email")
        password = self.ask_input("Password")
        return email, password

    def display_login_success(self):
        """Confirm successful login."""
        self.display_message("Login successful! Welcome.")

    def display_login_failure(self):
        """Warn about failed credentials."""
        self.display_error("Invalid email or password.")