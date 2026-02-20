# tests/test_robustness_edge_cases.py
"""
Integration tests for edge cases, permission denials, and coverage optimization.

List of tests:
- test_auth_controller_full_flow: Covers logout and failed login logic.
- test_auth_login_success: Covers successful login and session management.
- test_client_controller_unauthorized: Covers permission denial branches.
- test_contract_controller_ownership: Covers ownership and not found logic.
- test_event_controller_complex_rules: Covers unsigned contracts and support.
- test_controllers_list_methods: Covers list_all methods for all controllers.
- test_employee_management_denials: Covers admin-only creation/update logic.
- test_repository_integrity_failure: Covers DB constraints and rollbacks.
- test_repository_delete_logic: Covers the delete method in BaseRepository.
- test_repository_specialized_filters: Covers specific repository lookups.
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
from app.utils.auth import hash_password


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


def test_auth_login_success(db_session, auth_ctrl):
    """Covers successful login and user data structure."""
    dept = Department(name="AUTH_DEPT")
    db_session.add(dept)
    db_session.flush()

    pwd = hash_password("secret123")
    emp = Employee(
        full_name="Auth Success",
        email="success@test.com",
        password=pwd,
        employee_number="EMP_OK",
        department_id=dept.id
    )
    db_session.add(emp)
    db_session.commit()

    user = auth_ctrl.login("success@test.com", "secret123")
    assert user is not None
    # AuthController.login does not return 'email' in user_data dict
    assert user["full_name"] == "Auth Success"
    assert user["department"] == "AUTH_DEPT"


def test_client_controller_unauthorized(db_session, auth_ctrl):
    """Covers permission denial branches using manual session injection."""
    client_repo = ClientRepository(db_session)
    ctrl = ClientController(client_repo, auth_ctrl)

    # Support cannot create clients
    auth_ctrl.current_user_data = {"id": 1, "department": "SUPPORT"}
    assert ctrl.create_client({"full_name": "Fail", "phone": "123"}) is None

    # Sales cannot update unknown clients or others' clients
    auth_ctrl.current_user_data = {"id": 2, "department": "SALES"}
    assert ctrl.update_client(9999, {"full_name": "New"}) is None


def test_contract_controller_ownership(db_session, auth_ctrl):
    """Covers ownership and not found logic."""
    contract_repo = ContractRepository(db_session)
    ctrl = ContractController(contract_repo, auth_ctrl)

    sales_dept = Department(name="SALES")
    db_session.add(sales_dept)
    db_session.flush()

    emp5 = Employee(
        id=5, full_name="S1", email="s5@t.com", password="p",
        employee_number="E5", department_id=sales_dept.id
    )
    emp10 = Employee(
        id=10, full_name="S2", email="s10@t.com", password="p",
        employee_number="E10", department_id=sales_dept.id
    )
    db_session.add_all([emp5, emp10])
    db_session.flush()

    cl = Client(full_name="X", email="x@t.com", phone="1",
                company_name="X", sales_contact_id=5)
    db_session.add(cl)
    db_session.flush()

    c = Contract(id=102, sales_contact_id=10, client_id=cl.id,
                 total_amount=1000, remaining_amount=1000)
    db_session.add(c)
    db_session.flush()

    # User 5 tries to update user 10's contract
    auth_ctrl.current_user_data = {"id": 5, "department": "SALES"}
    assert ctrl.update_contract(102, {"total_amount": 2000}) is None


def test_event_controller_complex_rules(db_session, auth_ctrl):
    """Covers unsigned contracts and support assigned logic."""
    event_repo = EventRepository(db_session)
    ctrl = EventController(event_repo, auth_ctrl)

    s_dept = Department(name="SALES")
    sup_dept = Department(name="SUPPORT")
    db_session.add_all([s_dept, sup_dept])
    db_session.flush()

    s_emp = Employee(id=20, full_name="S1", email="s20@t.com", password="p",
                     employee_number="E20", department_id=s_dept.id)
    sup_emp = Employee(id=21, full_name="Sup1", email="s21@t.com", password="p",
                       employee_number="E21", department_id=sup_dept.id)
    db_session.add_all([s_emp, sup_emp])
    db_session.flush()

    cl = Client(full_name="Y", email="y@t.com", phone="2",
                company_name="Y", sales_contact_id=20)
    db_session.add(cl)
    db_session.flush()

    c = Contract(id=202, sales_contact_id=20, is_signed=False,
                 total_amount=0, remaining_amount=0, client_id=cl.id)
    db_session.add(c)
    db_session.flush()

    # Cannot create event for unsigned contract
    auth_ctrl.current_user_data = {"id": 20, "department": "SALES"}
    assert ctrl.create_event({"name": "X"}, c) is None

    ev = Event(id=302, name="Ev", location="P", attendees=5, notes="N",
               client_id=cl.id, contract_id=c.id, support_contact_id=sup_emp.id,
               event_date_start=datetime.now(), event_date_end=datetime.now())
    db_session.add(ev)
    db_session.flush()

    # Different support user cannot update
    auth_ctrl.current_user_data = {"id": 99, "department": "SUPPORT"}
    assert ctrl.update_event(302, {"notes": "hack"}) is None


def test_controllers_list_methods(db_session, auth_ctrl):
    """Covers list_all methods."""
    auth_ctrl.current_user_data = {"id": 1, "department": "MANAGEMENT"}

    cl_ctrl = ClientController(ClientRepository(db_session), auth_ctrl)
    assert isinstance(cl_ctrl.list_all_clients(), list)

    co_ctrl = ContractController(ContractRepository(db_session), auth_ctrl)
    assert co_ctrl.list_all_contracts() is not None

    ev_ctrl = EventController(EventRepository(db_session), auth_ctrl)
    assert ev_ctrl.list_all_events() is not None


def test_employee_management_denials(db_session, auth_ctrl):
    """Covers admin-only creation logic."""
    emp_repo = EmployeeRepository(db_session)
    ctrl = EmployeeController(emp_repo, auth_ctrl)
    auth_ctrl.current_user_data = {"department": "SALES"}
    assert ctrl.create_employee({"full_name": "Ghost"}) is None


def test_repository_integrity_failure(db_session):
    """Covers BaseRepository IntegrityError handling."""
    repo = ClientRepository(db_session)
    c1 = Client(full_name="A", email="dup@t.com", phone="1", company_name="C")
    db_session.add(c1)
    db_session.commit()

    c2 = Client(full_name="B", email="dup@t.com", phone="2", company_name="C")
    with pytest.raises(IntegrityError):
        repo.add(c2)


def test_repository_delete_logic(db_session):
    """Covers the delete method in BaseRepository."""
    repo = ClientRepository(db_session)
    cl = Client(full_name="Del", email="del@t.com", phone="0", company_name="D")
    db_session.add(cl)
    db_session.flush()
    repo.delete(cl)
    assert repo.get_by_id(cl.id) is None


def test_repository_specialized_filters(db_session):
    """Covers specific filter methods in repositories."""
    e_repo = EmployeeRepository(db_session)
    assert e_repo.get_by_email("none@t.com") is None

    c_repo = ContractRepository(db_session)
    assert isinstance(c_repo.get_unsigned_contracts(), list)

    ev_repo = EventRepository(db_session)
    assert isinstance(ev_repo.get_events_without_support(), list)


def test_models_string_representation():
    """Covers __repr__ for all models."""
    assert "Client" in repr(Client(full_name="Test"))
    assert "Contract" in repr(Contract(id=1))
    assert "Event" in repr(Event(name="Party"))
    assert "Employee" in repr(Employee(full_name="T", email="t@t.com"))