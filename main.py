# main.py
"""
Entry point for the Epic Events CRM application.
Manages the main loop and coordinate between controllers and views.
"""

from datetime import datetime

import sentry_sdk
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
from app.controllers.employee_controller import EmployeeController

from app.views.auth_view import AuthView
from app.views.main_menu_view import MainMenuView
from app.views.client_view import ClientView
from app.views.contract_view import ContractView
from app.views.event_view import EventView
from app.views.employee_view import EmployeeView

# Initialize Sentry
sentry_sdk.init(
    dsn=Config.SENTRY_DSN,
    # Set the environment (default to development if not specified in Config)
    environment=getattr(Config, "ENVIRONMENT", "development"),
    traces_sample_rate=1.0,
    profiles_sample_rate=1.0,
)


def main():
    """Main application execution logic."""
    try:
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
        emp_ctrl = EmployeeController(emp_repo, auth_ctrl)

        # Initialize Views
        auth_view = AuthView()
        menu_view = MainMenuView()
        client_view = ClientView()
        contract_view = ContractView()
        event_view = EventView()
        emp_view = EmployeeView()

        # 1. Authentication Check
        user_data = auth_ctrl.get_logged_in_user()
        if not user_data:
            email, password = auth_view.ask_login_details()
            user_data = auth_ctrl.login(email, password)
            if not user_data:
                auth_view.display_login_failure()
                return

        auth_view.display_login_success()

        # 2. Application Loop
        while True:

            menu_view.display_menu(user_data["department"])
            choice = menu_view.ask_menu_option()

            if choice == "1":
                data = client_ctrl.list_all_clients(user_data=user_data)
                client_view.display_clients(data)

            elif choice == "2":
                data = contract_ctrl.list_all_contracts(user_data=user_data)
                contract_view.display_contracts(data)

            elif choice == "3":
                data = event_ctrl.list_all_events(user_data=user_data)
                event_view.display_events(data)

            elif choice == "4":
                if user_data["department"] != "MANAGEMENT":
                    print("Invalid option. Please try again.")
                    continue
                data = emp_ctrl.list_all_employees(user_data=user_data)
                emp_view.display_employees(data)

            elif choice == "5":
                if user_data["department"] != "MANAGEMENT":
                    print("Invalid option. Please try again.")
                    continue
                details = emp_view.ask_employee_details()
                emp_ctrl.create_employee(
                    user_data=user_data,
                    employee_data=details
                )

            elif choice == "6":
                if user_data["department"] != "MANAGEMENT":
                    print("Invalid option. Please try again.")
                    continue
                emp_id = emp_view.ask_input("Enter Employee ID to update")
                if emp_id.isdigit():
                    updates = emp_view.ask_update_details()
                    emp_ctrl.update_employee(
                        user_data=user_data,
                        emp_id=int(emp_id),
                        update_data=updates
                    )

            elif choice == "7":
                if user_data["department"] != "MANAGEMENT":
                    print("Invalid option. Please try again.")
                    continue
                details = contract_view.ask_contract_details()
                contract_ctrl.create_contract(
                    user_data=user_data,
                    contract_data=details
                )

            elif choice == "8":
                if user_data["department"] != "MANAGEMENT":
                    print("Invalid option. Please try again.")
                    continue
                contract_id = contract_view.ask_input(
                    "Enter Contract ID to update"
                )
                if contract_id.isdigit():
                    updates = contract_view.ask_contract_update_details()
                    contract_ctrl.update_contract(
                        user_data=user_data,
                        contract_id=int(contract_id),
                        updates=updates
                    )

            elif choice == "9":
                if user_data["department"] != "MANAGEMENT":
                    print("Invalid option. Please try again.")
                    continue
                event_id = event_view.ask_input(
                    "Enter Event ID to assign support"
                )
                support_id = event_view.ask_input(
                    "Enter Support Employee ID"
                )
                if event_id.isdigit() and support_id.isdigit():
                    updates = {"support_contact_id": int(support_id)}
                    event_ctrl.update_event(
                        user_data=user_data,
                        event_id=int(event_id),
                        updates=updates
                    )

            elif choice == "10":
                if user_data["department"] != "MANAGEMENT":
                    print("Invalid option. Please try again.")
                    continue
                events = event_ctrl.list_all_events(
                    user_data=user_data
                ) or []
                no_support = [
                    event for event in events
                    if not event.support_contact_id
                ]
                event_view.display_events(no_support)

            elif choice == "20":
                if user_data["department"] != "SALES":
                    print("Invalid option. Please try again.")
                    continue
                details = client_view.ask_client_details()
                last_contact = details.get("last_contact", "").strip()
                if not last_contact:
                    details.pop("last_contact", None)
                else:
                    try:
                        details["last_contact"] = datetime.strptime(
                            last_contact,
                            "%Y-%m-%d %H:%M:%S",
                        )
                    except ValueError:
                        details.pop("last_contact", None)
                client_ctrl.create_client(
                    user_data=user_data,
                    client_data=details
                )

            elif choice == "21":
                if user_data["department"] != "SALES":
                    print("Invalid option. Please try again.")
                    continue
                client_id = client_view.ask_input(
                    "Enter Client ID to update"
                )
                if client_id.isdigit():
                    updates = client_view.ask_update_details()
                    client_ctrl.update_client(
                        user_data=user_data,
                        client_id=int(client_id),
                        updates=updates
                    )

            elif choice == "22":
                if user_data["department"] != "SALES":
                    print("Invalid option. Please try again.")
                    continue
                contract_id = contract_view.ask_input(
                    "Enter Contract ID to update"
                )
                if contract_id.isdigit():
                    updates = contract_view.ask_contract_update_details()
                    contract_ctrl.update_contract(
                        user_data=user_data,
                        contract_id=int(contract_id),
                        updates=updates
                    )

            elif choice == "23":
                if user_data["department"] != "SALES":
                    print("Invalid option. Please try again.")
                    continue
                contracts = contract_ctrl.list_all_contracts(
                    user_data=user_data
                ) or []
                unsigned = [
                    contract for contract in contracts
                    if not contract.is_signed
                ]
                contract_view.display_contracts(unsigned)

            elif choice == "24":
                if user_data["department"] != "SALES":
                    print("Invalid option. Please try again.")
                    continue
                contracts = contract_ctrl.list_all_contracts(
                    user_data=user_data
                ) or []
                unpaid = [
                    contract for contract in contracts
                    if contract.amount_due > 0
                ]
                contract_view.display_contracts(unpaid)

            elif choice == "25":
                if user_data["department"] != "SALES":
                    print("Invalid option. Please try again.")
                    continue
                details = event_view.ask_event_details()
                event_ctrl.create_event(
                    user_data=user_data,
                    event_data=details
                )

            elif choice == "30":
                if user_data["department"] != "SUPPORT":
                    print("Invalid option. Please try again.")
                    continue
                events = event_ctrl.list_all_events(
                    user_data=user_data
                ) or []
                my_events = [
                    event for event in events
                    if event.support_contact_id == user_data["id"]
                ]
                event_view.display_events(my_events)

            elif choice == "31":
                if user_data["department"] != "SUPPORT":
                    print("Invalid option. Please try again.")
                    continue
                event_id = event_view.ask_input(
                    "Enter Event ID to update"
                )
                if event_id.isdigit():
                    updates = event_view.ask_event_update_details()
                    event_ctrl.update_event(
                        user_data=user_data,
                        event_id=int(event_id),
                        updates=updates,
                    )

            elif choice == "0":
                auth_ctrl.logout()
                print("Goodbye!")
                break

            else:
                print("Invalid option. Please try again.")

    except Exception as e:
        sentry_sdk.capture_exception(e)
        print(f"A fatal error occurred: {e}")
        raise e


if __name__ == "__main__":
    main()