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
            # Capture user_data directly from login()
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
                # Pass user_data to satisfy the @require_auth decorator
                data = client_ctrl.list_all_clients(user_data=user_data)
                client_view.display_clients(data)
            elif choice == "2":
                # Pass user_data to satisfy the @require_auth decorator
                data = contract_ctrl.list_all_contracts(user_data=user_data)
                contract_view.display_contracts(data)
            elif choice == "3":
                # Pass user_data to satisfy the @require_auth decorator
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
                emp_ctrl.create_employee(user_data=user_data, employee_data=details)
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

                contract_data = contract_view.ask_contract_details()

                client_id_raw = str(contract_data.get("client_id", "")).strip()
                if not client_id_raw.isdigit():
                    continue
                client = client_ctrl.repository.get_by_id(int(client_id_raw))
                if not client:
                    print("Client not found.")
                    continue

                try:
                    total_amount = float(str(contract_data["total_amount"]).strip())
                    remaining_amount = float(
                        str(contract_data["remaining_amount"]).strip()
                    )
                except (KeyError, ValueError, TypeError):
                    continue

                is_signed_raw = str(contract_data.get("is_signed", "")).strip()
                is_signed = is_signed_raw.lower() in ["y", "yes"]

                payload = {
                    "client_id": client.id,
                    "sales_contact_id": client.sales_contact_id,
                    "total_amount": total_amount,
                    "remaining_amount": remaining_amount,
                    "is_signed": is_signed,
                }
                contract_ctrl.create_contract(
                    user_data=user_data,
                    contract_data=payload,
                )
            elif choice == "8":
                if user_data["department"] != "MANAGEMENT":
                    print("Invalid option. Please try again.")
                    continue

                contract_id = contract_view.ask_input("Enter Contract ID")
                if not contract_id.isdigit():
                    continue

                raw = contract_view.ask_contract_update_details()
                updates = {}

                total_amount_raw = str(raw.get("total_amount", "")).strip()
                if total_amount_raw:
                    try:
                        updates["total_amount"] = float(total_amount_raw)
                    except ValueError:
                        updates.pop("total_amount", None)

                remaining_raw = str(raw.get("remaining_amount", "")).strip()
                if remaining_raw:
                    try:
                        updates["remaining_amount"] = float(remaining_raw)
                    except ValueError:
                        updates.pop("remaining_amount", None)

                is_signed_raw = str(raw.get("is_signed", "")).strip().lower()
                if is_signed_raw in ["y", "yes"]:
                    updates["is_signed"] = True
                elif is_signed_raw in ["n", "no"]:
                    updates["is_signed"] = False

                if updates:
                    contract_ctrl.update_contract(
                        user_data=user_data,
                        contract_id=int(contract_id),
                        updates=updates,
                    )
            elif choice == "9":
                if user_data["department"] != "MANAGEMENT":
                    print("Invalid option. Please try again.")
                    continue
                event_id = event_view.ask_input("Enter Event ID")
                support_id = event_view.ask_input("Enter Support Employee ID")
                if not event_id.isdigit() or not support_id.isdigit():
                    continue
                updates = {"support_contact_id": int(support_id)}
                event_ctrl.update_event(
                    user_data=user_data,
                    event_id=int(event_id),
                    updates=updates,
                )
            elif choice == "10":
                if user_data["department"] != "MANAGEMENT":
                    print("Invalid option. Please try again.")
                    continue
                events = event_ctrl.list_events_without_support(
                    user_data=user_data
                ) or []
                event_view.display_events(events)
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
                client_ctrl.create_client(user_data=user_data, client_data=details)
            elif choice == "21":
                if user_data["department"] != "SALES":
                    print("Invalid option. Please try again.")
                    continue

                client_id = client_view.ask_input("Enter Client ID to update")
                if not client_id.isdigit():
                    continue

                raw = client_view.ask_client_update_details()
                updates = {}

                full_name = str(raw.get("full_name", "")).strip()
                email = str(raw.get("email", "")).strip()
                phone = str(raw.get("phone", "")).strip()
                company_name = str(raw.get("company_name", "")).strip()

                if full_name:
                    updates["full_name"] = full_name
                if email:
                    updates["email"] = email
                if phone:
                    updates["phone"] = phone
                if company_name:
                    updates["company_name"] = company_name

                last_contact = str(raw.get("last_contact", "")).strip()
                if last_contact:
                    try:
                        updates["last_contact"] = datetime.strptime(
                            last_contact,
                            "%Y-%m-%d %H:%M:%S",
                        )
                    except ValueError:
                        updates.pop("last_contact", None)

                if updates:
                    client_ctrl.update_client(
                        user_data=user_data,
                        client_id=int(client_id),
                        updates=updates,
                    )
            elif choice == "22":
                if user_data["department"] != "SALES":
                    print("Invalid option. Please try again.")
                    continue

                contract_id = contract_view.ask_input("Enter Contract ID")
                if not contract_id.isdigit():
                    continue

                raw = contract_view.ask_contract_update_details()
                updates = {}

                total_amount_raw = str(raw.get("total_amount", "")).strip()
                if total_amount_raw:
                    try:
                        updates["total_amount"] = float(total_amount_raw)
                    except ValueError:
                        updates.pop("total_amount", None)

                remaining_raw = str(raw.get("remaining_amount", "")).strip()
                if remaining_raw:
                    try:
                        updates["remaining_amount"] = float(remaining_raw)
                    except ValueError:
                        updates.pop("remaining_amount", None)

                is_signed_raw = str(raw.get("is_signed", "")).strip().lower()
                if is_signed_raw in ["y", "yes"]:
                    updates["is_signed"] = True
                elif is_signed_raw in ["n", "no"]:
                    updates["is_signed"] = False

                if updates:
                    contract_ctrl.update_contract(
                        user_data=user_data,
                        contract_id=int(contract_id),
                        updates=updates,
                    )
            elif choice == "23":
                if user_data["department"] != "SALES":
                    print("Invalid option. Please try again.")
                    continue
                contracts = contract_ctrl.list_unsigned_contracts(
                    user_data=user_data
                ) or []
                contract_view.display_contracts(contracts)
            elif choice == "24":
                if user_data["department"] != "SALES":
                    print("Invalid option. Please try again.")
                    continue
                contracts = contract_ctrl.list_unpaid_contracts(
                    user_data=user_data
                ) or []
                contract_view.display_contracts(contracts)
            elif choice == "25":
                if user_data["department"] != "SALES":
                    print("Invalid option. Please try again.")
                    continue

                contract_id_raw = event_view.ask_input("Enter Contract ID").strip()

                if not contract_id_raw.isdigit():
                    print("Invalid Contract ID. Please enter a numeric ID.")
                    continue

                contract = contract_ctrl.repository.get_by_id(int(contract_id_raw))
                if not contract:
                    print("Contract not found.")
                    continue

                # FAIL FAST business rules before asking event details
                if contract.sales_contact_id != user_data["id"]:
                    print(
                        "Access denied: you are not the sales contact for this "
                        "contract/client."
                    )
                    continue

                if not contract.is_signed:
                    print("Cannot create an event: the contract is not signed.")
                    continue

                raw = event_view.ask_event_details()

                def parse_dt(value: str):
                    value = value.strip()
                    if not value:
                        return None
                    # Accept short and full formats
                    for fmt in ("%Y-%m-%d %H", "%Y-%m-%d %H:%M:%S"):
                        try:
                            return datetime.strptime(value, fmt)
                        except ValueError:
                            continue
                    return None

                start_dt = parse_dt(str(raw.get("event_date_start", "")))
                end_dt = parse_dt(str(raw.get("event_date_end", "")))

                if not start_dt or not end_dt:
                    print(
                        "Invalid date format. Use 'YYYY-MM-DD HH' "
                        "or 'YYYY-MM-DD HH:MM:SS'."
                    )
                    continue

                if end_dt <= start_dt:
                    print("Invalid dates: event end must be after event start.")
                    continue

                attendees_raw = str(raw.get("attendees", "")).strip()
                try:
                    attendees = int(attendees_raw)
                except ValueError:
                    print("Invalid attendees value. Please enter a number.")
                    continue

                event_data = {
                    "name": str(raw.get("name", "")).strip(),
                    "event_date_start": start_dt,
                    "event_date_end": end_dt,
                    "location": str(raw.get("location", "")).strip(),
                    "attendees": attendees,
                    "notes": str(raw.get("notes", "")).strip(),
                    "client_id": contract.client_id,
                    "contract_id": contract.id,
                    "support_contact_id": None,
                }

                event_ctrl.create_event(
                    user_data=user_data,
                    event_data=event_data,
                    contract=contract,
                )
            elif choice == "30":
                if user_data["department"] != "SUPPORT":
                    print("Invalid option. Please try again.")
                    continue
                events = event_ctrl.list_my_events(user_data=user_data) or []
                event_view.display_events(events)
            elif choice == "31":
                if user_data["department"] != "SUPPORT":
                    print("Invalid option. Please try again.")
                    continue
                events = event_ctrl.list_my_events(user_data=user_data) or []
                event_view.display_events(events)

                event_id = event_view.ask_input("Enter Event ID to update")
                if not event_id.isdigit():
                    continue

                raw = event_view.ask_event_update_details()
                updates = {}

                notes = str(raw.get("notes", "")).strip()
                location = str(raw.get("location", "")).strip()
                attendees_raw = str(raw.get("attendees", "")).strip()

                if notes:
                    updates["notes"] = notes
                if location:
                    updates["location"] = location
                if attendees_raw:
                    try:
                        updates["attendees"] = int(attendees_raw)
                    except ValueError:
                        updates.pop("attendees", None)

                if updates:
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
        # Catch and report any fatal application errors
        sentry_sdk.capture_exception(e)
        print(f"A fatal error occurred: {e}")
        raise e


if __name__ == "__main__":
    main()