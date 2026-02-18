# main.py
"""
Entry point for the Epic Events CRM application.
Manages the main loop and coordinate between controllers and views.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config.config import Config

from app.repositories.employee_repository import EmployeeRepository
from app.repositories.client_repository import ClientRepository
from app.repositories.contract_repository import ContractRepository
from app.repositories.event_repository import EventRepository

from app.controllers.auth_controller import AuthController
from app.controllers.client_controller import ClientController
from app.controllers.contract_controller import ContractController
from app.controllers.event_controller import EventController

from app.views.auth_view import AuthView
from app.views.main_menu_view import MainMenuView
from app.views.client_view import ClientView
from app.views.contract_view import ContractView
from app.views.event_view import EventView


def main():
    """Main application execution logic."""
    # Database Setup
    engine = create_engine(Config.get_db_url())
    session_factory = sessionmaker(bind=engine)
    session = session_factory()

    # Initialize Repositories
    emp_repo = EmployeeRepository(session)
    client_repo = ClientRepository(session)
    contract_repo = ContractRepository(session)
    event_repo = EventRepository(session)

    # Initialize Controllers
    auth_ctrl = AuthController(emp_repo)
    client_ctrl = ClientController(client_repo, auth_ctrl)
    contract_ctrl = ContractController(contract_repo, auth_ctrl)
    event_ctrl = EventController(event_repo, auth_ctrl)

    # Initialize Views
    auth_view = AuthView()
    menu_view = MainMenuView()
    client_view = ClientView()
    contract_view = ContractView()
    event_view = EventView()

    # 1. Authentication Check
    user_data = auth_ctrl.get_logged_in_user()
    if not user_data:
        email, password = auth_view.ask_login_details()
        if auth_ctrl.login(email, password):
            user_data = auth_ctrl.get_logged_in_user()
        else:
            auth_view.display_login_failure()
            return

    auth_view.display_login_success()

    # 2. Application Loop
    while True:
        menu_view.display_menu(user_data["department"])
        choice = menu_view.ask_menu_option()

        if choice == "1":
            data = client_ctrl.list_all_clients()
            client_view.display_clients(data)
        elif choice == "2":
            data = contract_ctrl.list_all_contracts()
            contract_view.display_contracts(data)
        elif choice == "3":
            data = event_ctrl.list_all_events()
            event_view.display_events(data)
        elif choice == "0":
            auth_ctrl.logout()
            print("Goodbye!")
            break
        else:
            print("Invalid option. Please try again.")


if __name__ == "__main__":
    main()