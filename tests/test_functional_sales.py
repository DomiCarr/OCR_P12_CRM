# tests/test_functional_sales.py
"""
Functional tests for Sales (T13) operations.

List of tests:
- test_sales_can_create_client: Verify client creation and auto-assignment (6.8).
- test_support_cannot_create_client: Verify permission restriction for creation.
- test_sales_can_update_own_client: Success for assigned contact (6.9).
- test_sales_cannot_update_other_client: Denied for non-assigned contact.
- test_management_can_create_contract: Verify contract creation by management (6.10).
- test_sales_can_sign_own_contract: Verify sales can update their assigned
  contracts (6.11).
- test_sales_can_create_event_for_signed_contract: Success if signed and owner
  (6.12).
- test_sales_cannot_create_event_for_unsigned_contract: Denied if not signed
  (6.12).
- test_support_can_update_assigned_event: Verify support can update their event
  (6.13).
"""

import uuid
import pytest
from datetime import datetime, timedelta
from sqlalchemy import select
from app.controllers.client_controller import ClientController
from app.controllers.contract_controller import ContractController
from app.controllers.event_controller import EventController
from app.controllers.auth_controller import AuthController
from app.repositories.client_repository import ClientRepository
from app.repositories.contract_repository import ContractRepository
from app.repositories.event_repository import EventRepository
from app.repositories.employee_repository import EmployeeRepository
from app.models.department import Department
from app.models.employee import Employee
from app.models.client import Client
from app.models.contract import Contract
from app.models.event import Event
from app.repositories.base_repository import BaseRepository


@pytest.fixture
def sales_suite(db_session):
    """Setup repositories and controllers for sales tests."""
    dept_repo = BaseRepository(db_session, Department)
    emp_repo = EmployeeRepository(db_session)
    client_repo = ClientRepository(db_session)
    contract_repo = ContractRepository(db_session)
    event_repo = EventRepository(db_session)

    auth_ctrl = AuthController(emp_repo)
    client_ctrl = ClientController(client_repo, auth_ctrl)
    contract_ctrl = ContractController(contract_repo, auth_ctrl)
    event_ctrl = EventController(event_repo, auth_ctrl)

    # Setup departments
    for name in ["SALES", "MANAGEMENT", "SUPPORT"]:
        if not db_session.execute(
            select(Department).filter_by(name=name)
        ).scalar():
            dept_repo.add(Department(name=name))

    sales_dept = db_session.execute(
        select(Department).filter_by(name="SALES")
    ).scalar()
    mgmt_dept = db_session.execute(
        select(Department).filter_by(name="MANAGEMENT")
    ).scalar()
    supp_dept = db_session.execute(
        select(Department).filter_by(name="SUPPORT")
    ).scalar()

    # Employees
    unique_s1 = uuid.uuid4().hex[:4]
    s1 = emp_repo.add(Employee(
        full_name="Sales One", email=f"s1_{unique_s1}@crm.com",
        password="p", employee_number=f"S1_{unique_s1}",
        department_id=sales_dept.id
    ))

    unique_s2 = uuid.uuid4().hex[:4]
    s2 = emp_repo.add(Employee(
        full_name="Sales Two", email=f"s2_{unique_s2}@crm.com",
        password="p", employee_number=f"S2_{unique_s2}",
        department_id=sales_dept.id
    ))

    unique_m = uuid.uuid4().hex[:4]
    mgmt = emp_repo.add(Employee(
        full_name="Mgmt User", email=f"m1_{unique_m}@crm.com",
        password="p", employee_number=f"M1_{unique_m}",
        department_id=mgmt_dept.id
    ))

    unique_supp = uuid.uuid4().hex[:4]
    supp = emp_repo.add(Employee(
        full_name="Support User", email=f"supp_{unique_supp}@crm.com",
        password="p", employee_number=f"SUP_{unique_supp}",
        department_id=supp_dept.id
    ))

    # Seed baseline client/contract used by tests with hardcoded IDs
    baseline_client = client_repo.add(Client(
        full_name="Baseline Client",
        email=f"baseline_{uuid.uuid4().hex[:6]}@crm.com",
        phone="000",
        company_name="Baseline Corp",
        sales_contact_id=s1.id
    ))

    contract_repo.add(Contract(
        total_amount=1000,
        remaining_amount=1000,
        is_signed=True,
        client_id=baseline_client.id,
        sales_contact_id=s1.id
    ))

    return {
        "client_ctrl": client_ctrl,
        "contract_ctrl": contract_ctrl,
        "event_ctrl": event_ctrl,
        "sales_1": s1,
        "sales_2": s2,
        "mgmt_user": mgmt,
        "supp_user": supp
    }


def test_sales_can_create_client(sales_suite):
    """Verify that a SALES user can create a client with auto-assignment."""
    ctrl = sales_suite["client_ctrl"]
    user = sales_suite["sales_1"]
    user_data = {"id": user.id, "department": "SALES"}
    client_data = {
        "full_name": "Test Client Inc",
        "email": f"contact_{uuid.uuid4().hex[:6]}@client.com",
        "phone": "0102030405",
        "company_name": "Test Corp"
    }
    new_client = ctrl.create_client(user_data=user_data, client_data=client_data)
    assert new_client is not None
    assert new_client.sales_contact_id == user.id


def test_support_cannot_create_client(sales_suite):
    """Verify that a SUPPORT user cannot create a client."""
    ctrl = sales_suite["client_ctrl"]
    user_data = {"id": 999, "department": "SUPPORT"}
    client_data = {
        "full_name": "Forbidden",
        "email": "f@client.com",
        "phone": "0000",
        "company_name": "No Access"
    }
    result = ctrl.create_client(user_data=user_data, client_data=client_data)
    assert result is None


def test_sales_can_update_own_client(sales_suite):
    """Verify sales can update their assigned client."""
    ctrl = sales_suite["client_ctrl"]
    s1 = sales_suite["sales_1"]
    user_data = {"id": s1.id, "department": "SALES"}

    client_data = {
        "full_name": "Owned Client",
        "email": f"c_{uuid.uuid4().hex[:4]}@c.com",
        "phone": "12345",
        "company_name": "Own Corp",
        "sales_contact_id": s1.id
    }
    client = ctrl.create_client(user_data=user_data, client_data=client_data)

    updated = ctrl.update_client(
        user_data=user_data,
        client_id=client.id,
        updates={"phone": "99999"}
    )
    assert updated is not None
    assert updated.phone == "99999"


def test_sales_cannot_update_other_client(sales_suite):
    """Verify sales cannot update a client assigned to someone else."""
    ctrl = sales_suite["client_ctrl"]
    s1 = sales_suite["sales_1"]
    s2 = sales_suite["sales_2"]

    client_data = {
        "full_name": "S1 Client",
        "email": f"c_{uuid.uuid4().hex[:4]}@c.com",
        "phone": "123",
        "company_name": "S1 Corp",
        "sales_contact_id": s1.id
    }
    client = ctrl.create_client(
        user_data={"id": s1.id, "department": "SALES"},
        client_data=client_data
    )

    result = ctrl.update_client(
        user_data={"id": s2.id, "department": "SALES"},
        client_id=client.id,
        updates={"phone": "000"}
    )
    assert result is None


def test_management_can_create_contract(sales_suite):
    """Verify that MANAGEMENT can create a contract for a client."""
    client_ctrl = sales_suite["client_ctrl"]
    contract_ctrl = sales_suite["contract_ctrl"]
    sales_user = sales_suite["sales_1"]
    mgmt_user = sales_suite["mgmt_user"]

    client = client_ctrl.create_client(
        user_data={"id": sales_user.id, "department": "SALES"},
        client_data={
            "full_name": "Contract Client",
            "email": f"c_{uuid.uuid4().hex[:4]}@c.com",
            "phone": "0600000000",
            "company_name": "Contract Corp"
        }
    )

    contract_data = {
        "total_amount": 1000.00,
        "remaining_amount": 1000.00,
        "is_signed": False,
        "client_id": client.id,
        "sales_contact_id": sales_user.id
    }

    new_contract = contract_ctrl.create_contract(
        user_data={"id": mgmt_user.id, "department": "MANAGEMENT"},
        contract_data=contract_data
    )

    assert new_contract is not None
    assert float(new_contract.total_amount) == 1000.00


def test_sales_can_sign_own_contract(sales_suite):
    """Verify that sales can sign a contract assigned to them."""
    client_ctrl = sales_suite["client_ctrl"]
    contract_ctrl = sales_suite["contract_ctrl"]
    sales_user = sales_suite["sales_1"]
    user_data = {"id": sales_user.id, "department": "SALES"}

    client = client_ctrl.create_client(
        user_data=user_data,
        client_data={
            "full_name": "Sign Client",
            "email": f"c_{uuid.uuid4().hex[:4]}@c.com",
            "phone": "0611111111",
            "company_name": "Sign Corp"
        }
    )

    contract = contract_ctrl.repository.add(Contract(
        total_amount=500,
        remaining_amount=500,
        is_signed=False,
        client_id=client.id,
        sales_contact_id=sales_user.id
    ))

    updated = contract_ctrl.update_contract(
        user_data=user_data,
        contract_id=contract.id,
        updates={"is_signed": True}
    )

    assert updated is not None
    assert updated.is_signed is True


def test_sales_can_create_event_for_signed_contract(sales_suite):
    """Verify event creation works for a signed contract (6.12)."""
    event_ctrl = sales_suite["event_ctrl"]
    contract_ctrl = sales_suite["contract_ctrl"]
    sales_user = sales_suite["sales_1"]
    user_data = {"id": sales_user.id, "department": "SALES"}

    client = sales_suite["client_ctrl"].create_client(
        user_data=user_data,
        client_data={
            "full_name": "Event Client",
            "email": f"e_{uuid.uuid4().hex[:4]}@c.com",
            "phone": "06",
            "company_name": "Event Corp"
        }
    )

    contract = contract_ctrl.repository.add(Contract(
        total_amount=1000,
        remaining_amount=1000,
        is_signed=True,
        client_id=client.id,
        sales_contact_id=sales_user.id
    ))

    event_data = {
        "name": "Launch Party",
        "event_date_start": datetime.now(),
        "event_date_end": datetime.now() + timedelta(hours=2),
        "location": "Paris",
        "attendees": 50,
        "notes": "Test notes",
        "client_id": client.id,
        "contract_id": contract.id
    }

    event = event_ctrl.create_event(
        user_data=user_data,
        event_data=event_data,
        contract=contract
    )
    assert event is not None
    assert event.name == "Launch Party"


def test_sales_cannot_create_event_for_unsigned_contract(sales_suite):
    """Verify event creation is blocked if contract is not signed (6.12)."""
    event_ctrl = sales_suite["event_ctrl"]
    sales_user = sales_suite["sales_1"]
    user_data = {"id": sales_user.id, "department": "SALES"}

    contract = Contract(is_signed=False, sales_contact_id=sales_user.id)

    event = event_ctrl.create_event(
        user_data=user_data,
        event_data={},
        contract=contract
    )
    assert event is None


def test_support_can_update_assigned_event(sales_suite):
    """Verify support can update an event assigned to them (6.13)."""
    event_ctrl = sales_suite["event_ctrl"]
    supp_user = sales_suite["supp_user"]
    user_data = {"id": supp_user.id, "department": "SUPPORT"}

    # Setup: Create manual event assigned to supp_user
    new_event = event_ctrl.repository.add(Event(
        name="Update Test",
        event_date_start=datetime.now(),
        event_date_end=datetime.now(),
        location="Lyon",
        attendees=10,
        notes="Initial",
        client_id=1,
        contract_id=1,
        support_contact_id=supp_user.id
    ))

    updated = event_ctrl.update_event(
        user_data=user_data,
        event_id=new_event.id,
        updates={"notes": "Updated notes"}
    )

    assert updated is not None
    assert updated.notes == "Updated notes"
