# tests/test_controllers_negative_paths.py
"""
Extra controller tests to cover negative/early-return branches:
- permission denied
- not found
- business rule denials (ownership, unsigned contract, support assignment)

Goal: increase controller coverage without changing production code.
"""

from __future__ import annotations

from datetime import datetime, timedelta
import uuid

import pytest

from app.controllers.client_controller import ClientController
from app.controllers.contract_controller import ContractController
from app.controllers.employee_controller import EmployeeController
from app.controllers.event_controller import EventController

from app.models.client import Client
from app.models.contract import Contract
from app.models.department import Department
from app.models.employee import Employee
from app.models.event import Event

from app.repositories.base_repository import BaseRepository
from app.repositories.client_repository import ClientRepository
from app.repositories.contract_repository import ContractRepository
from app.repositories.employee_repository import EmployeeRepository
from app.repositories.event_repository import EventRepository


class DummyAuthController:
    """
    Minimal auth controller stub.
    Controllers only rely on:
      - current_user_data attribute
      - check_user_permission(action) -> bool
    """

    def __init__(self, allowed: set[str] | None = None):
        self.allowed = allowed or set()
        self.current_user_data = None

    def check_user_permission(self, action: str) -> bool:
        return action in self.allowed


@pytest.fixture
def seeded_staff(db_session):
    """Create departments + a few employees to use in controller tests."""
    dept_repo = BaseRepository(db_session, Department)

    d_sales = dept_repo.add(Department(name=f"SALES_{uuid.uuid4().hex[:6]}"))
    d_support = dept_repo.add(Department(name=f"SUPPORT_{uuid.uuid4().hex[:6]}"))
    d_mgmt = dept_repo.add(Department(name=f"MANAGEMENT_{uuid.uuid4().hex[:6]}"))

    sales = Employee(
        full_name="Sales User",
        email=f"sales_{uuid.uuid4().hex[:6]}@t.com",
        password="hashed",
        employee_number=f"S{uuid.uuid4().hex[:6]}",
        department_id=d_sales.id,
    )
    support = Employee(
        full_name="Support User",
        email=f"support_{uuid.uuid4().hex[:6]}@t.com",
        password="hashed",
        employee_number=f"U{uuid.uuid4().hex[:6]}",
        department_id=d_support.id,
    )
    mgmt = Employee(
        full_name="Mgmt User",
        email=f"mgmt_{uuid.uuid4().hex[:6]}@t.com",
        password="hashed",
        employee_number=f"M{uuid.uuid4().hex[:6]}",
        department_id=d_mgmt.id,
    )

    db_session.add_all([sales, support, mgmt])
    db_session.commit()

    return {"sales": sales, "support": support, "mgmt": mgmt}


@pytest.fixture
def seeded_business(db_session, seeded_staff):
    """Create a client + contracts + event to test controller rules."""
    staff = seeded_staff
    sales = staff["sales"]
    support = staff["support"]

    client = Client(
        full_name="Client A",
        email=f"client_{uuid.uuid4().hex[:6]}@t.com",
        phone="0102030405",
        company_name="Corp",
        sales_contact_id=sales.id,
    )
    db_session.add(client)
    db_session.commit()

    signed_contract = Contract(
        total_amount=1000,
        remaining_amount=100,
        is_signed=True,
        client_id=client.id,
        sales_contact_id=sales.id,
    )
    unsigned_contract = Contract(
        total_amount=500,
        remaining_amount=500,
        is_signed=False,
        client_id=client.id,
        sales_contact_id=sales.id,
    )
    db_session.add_all([signed_contract, unsigned_contract])
    db_session.commit()

    event = Event(
        name="Event A",
        event_date_start=datetime.now() + timedelta(days=1),
        event_date_end=datetime.now() + timedelta(days=2),
        location="Paris",
        attendees=10,
        notes="n",
        client_id=client.id,
        contract_id=signed_contract.id,
        support_contact_id=support.id,
    )
    db_session.add(event)
    db_session.commit()

    return {
        "client": client,
        "signed_contract": signed_contract,
        "unsigned_contract": unsigned_contract,
        "event": event,
    }


def test_client_controller_list_denied_returns_empty(db_session):
    auth = DummyAuthController(allowed=set())
    ctrl = ClientController(ClientRepository(db_session), auth)

    out = ctrl.list_all_clients(user_data={"id": 1, "department": "SALES"})
    assert out == []


def test_client_controller_update_denied_returns_none(db_session, seeded_business):
    auth = DummyAuthController(allowed=set())
    ctrl = ClientController(ClientRepository(db_session), auth)

    client = seeded_business["client"]
    out = ctrl.update_client(
        user_data={"id": client.sales_contact_id, "department": "SALES"},
        client_id=client.id,
        updates={"phone": "0999"},
    )
    assert out is None


def test_client_controller_update_not_found_returns_none(db_session):
    auth = DummyAuthController(allowed={"update_client"})
    ctrl = ClientController(ClientRepository(db_session), auth)

    out = ctrl.update_client(
        user_data={"id": 1, "department": "SALES"},
        client_id=999999,
        updates={"phone": "0999"},
    )
    assert out is None


def test_client_controller_update_denied_when_not_owner_and_not_mgmt(
    db_session, seeded_staff, seeded_business
):
    auth = DummyAuthController(allowed={"update_client"})
    ctrl = ClientController(ClientRepository(db_session), auth)

    client = seeded_business["client"]
    other_sales = seeded_staff["mgmt"]  # id differs from sales_contact_id
    user = {"id": other_sales.id, "department": "SALES"}

    out = ctrl.update_client(user_data=user, client_id=client.id, updates={"phone": "0999"})
    assert out is None


def test_contract_controller_create_denied_returns_none(db_session, seeded_business):
    auth = DummyAuthController(allowed=set())
    ctrl = ContractController(ContractRepository(db_session), auth)

    client = seeded_business["client"]
    out = ctrl.create_contract(
        user_data={"id": client.sales_contact_id, "department": "SALES"},
        contract_data={
            "total_amount": 100,
            "remaining_amount": 50,
            "is_signed": False,
            "client_id": client.id,
            "sales_contact_id": client.sales_contact_id,
        },
    )
    assert out is None


def test_contract_controller_update_not_found_returns_none(db_session):
    auth = DummyAuthController(allowed={"update_contract"})
    ctrl = ContractController(ContractRepository(db_session), auth)

    out = ctrl.update_contract(
        user_data={"id": 1, "department": "SALES"},
        contract_id=999999,
        updates={"remaining_amount": 0},
    )
    assert out is None


def test_employee_controller_create_denied_returns_none(db_session):
    auth = DummyAuthController(allowed=set())
    ctrl = EmployeeController(EmployeeRepository(db_session), auth)

    out = ctrl.create_employee(
        user_data={"id": 1, "department": "SALES"},
        employee_data={
            "full_name": "X",
            "email": f"x_{uuid.uuid4().hex[:6]}@t.com",
            "password": "pw",
            "employee_number": f"E{uuid.uuid4().hex[:6]}",
            "department_id": 1,
        },
    )
    assert out is None


def test_employee_controller_update_not_found_returns_none(db_session):
    auth = DummyAuthController(allowed={"update_employee"})
    ctrl = EmployeeController(EmployeeRepository(db_session), auth)

    out = ctrl.update_employee(
        user_data={"id": 1, "department": "MANAGEMENT"},
        emp_id=999999,
        update_data={"full_name": "New"},
    )
    assert out is None


def test_event_controller_create_denied_when_not_owner(db_session, seeded_staff, seeded_business):
    auth = DummyAuthController(allowed={"create_event"})
    ctrl = EventController(EventRepository(db_session), auth)

    contract = seeded_business["signed_contract"]
    not_owner = seeded_staff["support"]

    out = ctrl.create_event(
        user_data={"id": not_owner.id, "department": "SUPPORT"},
        event_data={
            "name": "Denied Event",
            "event_date_start": datetime.now() + timedelta(days=1),
            "event_date_end": datetime.now() + timedelta(days=2),
            "location": "Paris",
            "attendees": 10,
            "notes": "n",
            "client_id": contract.client_id,
            "contract_id": contract.id,
        },
        contract=contract,
    )
    assert out is None


def test_event_controller_create_denied_when_contract_unsigned(db_session, seeded_staff, seeded_business):
    auth = DummyAuthController(allowed={"create_event"})
    ctrl = EventController(EventRepository(db_session), auth)

    contract = seeded_business["unsigned_contract"]
    owner = seeded_staff["sales"]

    out = ctrl.create_event(
        user_data={"id": owner.id, "department": "SALES"},
        event_data={
            "name": "Denied Unsigned",
            "event_date_start": datetime.now() + timedelta(days=1),
            "event_date_end": datetime.now() + timedelta(days=2),
            "location": "Paris",
            "attendees": 10,
            "notes": "n",
            "client_id": contract.client_id,
            "contract_id": contract.id,
        },
        contract=contract,
    )
    assert out is None


def test_event_controller_update_denied_when_not_assigned_and_not_mgmt(
    db_session, seeded_staff, seeded_business
):
    auth = DummyAuthController(allowed={"update_event"})
    ctrl = EventController(EventRepository(db_session), auth)

    event = seeded_business["event"]
    not_assigned = seeded_staff["sales"]  # event.support_contact_id is support

    out = ctrl.update_event(
        user_data={"id": not_assigned.id, "department": "SALES"},
        event_id=event.id,
        updates={"notes": "x"},
    )
    assert out is None


def test_event_controller_update_not_found_returns_none(db_session):
    auth = DummyAuthController(allowed={"update_event"})
    ctrl = EventController(EventRepository(db_session), auth)

    out = ctrl.update_event(
        user_data={"id": 1, "department": "MANAGEMENT"},
        event_id=999999,
        updates={"notes": "x"},
    )
    assert out is None