"""
Integration tests for edge cases, permission denials, and repository exceptions.

List of tests:
- test_auth_controller_full_flow: Covers logout and failed login logic.
- test_client_controller_unauthorized: Covers permission denial branches.
- test_contract_controller_ownership: Covers ownership and not found logic.
- test_event_controller_complex_rules: Covers unsigned contracts and support.
- test_employee_management_denials: Covers admin-only creation/update logic.
- test_repository_integrity_failure: Covers DB constraints and rollbacks.
- test_models_string_representation: Covers __repr__ methods for all models.
"""

from datetime import datetime
import pytest
from sqlalchemy.exc import IntegrityError
from app.controllers.auth_controller import AuthController
from app.controllers.client_controller import ClientController
from app.controllers.contract_controller import ContractController
from app.controllers.event_controller import EventController
from app.controllers.employee_controller import EmployeeController
from app.repositories.employee_repository import EmployeeRepository
from app.repositories.client_repository import ClientRepository
from app.repositories.contract_repository import ContractRepository
from app.repositories.event_repository import EventRepository
from app.models.employee import Employee
from app.models.client import Client
from app.models.contract import Contract
from app.models.event import Event
from app.models.department import Department


@pytest.fixture
def auth_ctrl(db_session):
    """Fixture for AuthController."""
    return AuthController(EmployeeRepository(db_session))


def test_auth_controller_full_flow(auth_ctrl):
    """Covers logout and failed login logic."""
    auth_ctrl.logout()
    assert auth_ctrl.current_user_data is None
    assert auth_ctrl.login("ghost@missing.com", "password") is None
    assert auth_ctrl.check_user_permission("read") is False


def test_client_controller_unauthorized(db_session, auth_ctrl):
    """Covers permission denial branches."""
    client_repo = ClientRepository(db_session)
    ctrl = ClientController(client_repo, auth_ctrl)
    user_support = {"id": 1, "department": "SUPPORT"}
    assert ctrl.create_client(user_support, {"full_name": "Fail"}) in [None, []]
    user_sales = {"id": 2, "department": "SALES"}
    assert ctrl.update_client(user_sales, 9999, {"full_name": "New"}) in [None, []]


def test_contract_controller_ownership(db_session, auth_ctrl):
    """Covers ownership and not found logic."""
    contract_repo = ContractRepository(db_session)
    ctrl = ContractController(contract_repo, auth_ctrl)
    user_sales = {"id": 5, "department": "SALES"}

    # Create Department
    sales_dept = Department(name="SALES_OWN")
    db_session.add(sales_dept)
    db_session.flush()

    # Create two employees to avoid FK issues with sales_contact_id
    emp5 = Employee(
        id=5,
        full_name="Sales Guy",
        email="s5@t.com",
        password="password",
        employee_number="EMP005",
        department_id=sales_dept.id
    )
    emp10 = Employee(
        id=10,
        full_name="Other Sales",
        email="s10@t.com",
        password="password",
        employee_number="EMP010",
        department_id=sales_dept.id
    )
    db_session.add_all([emp5, emp10])
    db_session.flush()

    cl = Client(
        full_name="X",
        email="x@t.com",
        phone="1",
        company_name="X",
        sales_contact_id=5
    )
    db_session.add(cl)
    db_session.flush()

    other_contract = Contract(
        id=102,
        sales_contact_id=10,
        client_id=cl.id,
        total_amount=1000,
        remaining_amount=1000
    )
    db_session.add(other_contract)
    db_session.flush()
    assert ctrl.update_contract(user_sales, 102, {"total_amount": 2000}) in [None, []]


def test_event_controller_complex_rules(db_session, auth_ctrl):
    """Covers unsigned contracts and support assigned logic."""
    event_repo = EventRepository(db_session)
    ctrl = EventController(event_repo, auth_ctrl)

    sales_dept = Department(name="SALES_RULE")