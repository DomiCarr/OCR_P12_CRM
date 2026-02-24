# tests/test_controllers_more_more_coverage.py
"""
Extra controller tests to push coverage further (happy-path + extra branches),
without breaking non-regression.

Important:
- Fixtures are defined locally (pytest does NOT share fixtures across test files
  unless they are in conftest.py).
- Keep data compliant with DB constraints (e.g. Client.phone is NOT NULL).
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

from app.repositories.client_repository import ClientRepository
from app.repositories.contract_repository import ContractRepository
from app.repositories.employee_repository import EmployeeRepository
from app.repositories.event_repository import EventRepository

from app.utils.auth import verify_password


class DummyAuthController:
    """Minimal auth controller to drive controller permission branches."""

    def __init__(self, allowed: set[str]):
        self.allowed = allowed
        self.current_user_data: dict | None = None

    def check_user_permission(self, permission: str) -> bool:
        return permission in self.allowed


@pytest.fixture
def seeded_staff(db_session):
    """Create SALES / SUPPORT / MANAGEMENT employees."""
    sales_dept = Department(name=f"SALES_{uuid.uuid4().hex[:6]}")
    support_dept = Department(name=f"SUPPORT_{uuid.uuid4().hex[:6]}")
    mgmt_dept = Department(name=f"MANAGEMENT_{uuid.uuid4().hex[:6]}")
    db_session.add_all([sales_dept, support_dept, mgmt_dept])
    db_session.flush()

    sales = Employee(
        full_name="Sales User",
        email=f"sales_{uuid.uuid4().hex[:6]}@t.com",
        password="pw",
        employee_number=f"S{uuid.uuid4().hex[:6]}",
        department_id=sales_dept.id,
    )
    support = Employee(
        full_name="Support User",
        email=f"support_{uuid.uuid4().hex[:6]}@t.com",
        password="pw",
        employee_number=f"U{uuid.uuid4().hex[:6]}",
        department_id=support_dept.id,
    )
    mgmt = Employee(
        full_name="Mgmt User",
        email=f"mgmt_{uuid.uuid4().hex[:6]}@t.com",
        password="pw",
        employee_number=f"M{uuid.uuid4().hex[:6]}",
        department_id=mgmt_dept.id,
    )

    db_session.add_all([sales, support, mgmt])
    db_session.commit()

    return {"sales": sales, "support": support, "mgmt": mgmt}


@pytest.fixture
def seeded_business(db_session, seeded_staff):
    """Create a client + 2 contracts + 1 event for controller tests."""
    staff = seeded_staff
    sales = staff["sales"]
    support = staff["support"]

    client = Client(
        full_name="Client Seed",
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
        name="Event Seed",
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


def test_client_controller_list_all_clients_allowed_returns_clients(
    db_session, seeded_business
):
    auth = DummyAuthController(allowed={"read_client"})
    ctrl = ClientController(ClientRepository(db_session), auth)

    out = ctrl.list_all_clients(user_data={"id": 1, "department": "SALES"})
    assert isinstance(out, list)
    assert len(out) >= 1


def test_client_controller_create_success_sets_last_contact_and_prints(
    db_session, seeded_staff, capsys
):
    auth = DummyAuthController(allowed={"create_client"})
    ctrl = ClientController(ClientRepository(db_session), auth)

    sales = seeded_staff["sales"]
    created = ctrl.create_client(
        user_data={"id": sales.id, "department": "SALES"},
        client_data={
            "full_name": "New Client",
            "email": f"new_{uuid.uuid4().hex[:6]}@t.com",
            "phone": "0600000000",
            "company_name": "NewCorp",
        },
    )
    captured = capsys.readouterr().out

    assert created is not None
    assert created.sales_contact_id == sales.id
    assert created.last_contact is not None
    assert "client" in captured.lower()
    assert "created" in captured.lower()


def test_client_controller_update_success_as_owner_prints(
    db_session, seeded_business, capsys
):
    auth = DummyAuthController(allowed={"update_client"})
    ctrl = ClientController(ClientRepository(db_session), auth)

    client = seeded_business["client"]
    updated = ctrl.update_client(
        user_data={"id": client.sales_contact_id, "department": "SALES"},
        client_id=client.id,
        updates={"phone": "0999999999"},
    )
    captured = capsys.readouterr().out

    assert updated is not None
    assert updated.phone == "0999999999"
    assert "updated" in captured.lower()


def test_contract_controller_create_infers_sales_contact_from_client(
    db_session, seeded_business, seeded_staff
):
    auth = DummyAuthController(allowed={"create_contract"})
    ctrl = ContractController(ContractRepository(db_session), auth)

    client = seeded_business["client"]
    mgmt = seeded_staff["mgmt"]

    contract = ctrl.create_contract(
        user_data={"id": mgmt.id, "department": "MANAGEMENT"},
        contract_data={
            "total_amount": 2500,
            "remaining_amount": 2500,
            "is_signed": False,
            "client_id": client.id,
            # intentionally omit sales_contact_id to hit the "infer" branch
        },
    )

    assert contract is not None
    assert contract.client_id == client.id
    assert contract.sales_contact_id == client.sales_contact_id


def test_contract_controller_create_missing_client_id_returns_none(
    db_session, seeded_staff
):
    auth = DummyAuthController(allowed={"create_contract"})
    ctrl = ContractController(ContractRepository(db_session), auth)

    mgmt = seeded_staff["mgmt"]
    out = ctrl.create_contract(
        user_data={"id": mgmt.id, "department": "MANAGEMENT"},
        contract_data={"total_amount": 10, "remaining_amount": 10},
    )
    assert out is None


def test_contract_controller_update_denied_when_not_owner_and_not_mgmt(
    db_session, seeded_business, seeded_staff
):
    auth = DummyAuthController(allowed={"update_contract"})
    ctrl = ContractController(ContractRepository(db_session), auth)

    contract = seeded_business["signed_contract"]
    other_sales = seeded_staff["support"]  # wrong user + wrong dept for ownership

    out = ctrl.update_contract(
        user_data={"id": other_sales.id, "department": "SUPPORT"},
        contract_id=contract.id,
        updates={"total_amount": 9999},
    )
    assert out is None


def test_employee_controller_update_hashes_password(db_session, seeded_staff):
    auth = DummyAuthController(allowed={"update_employee"})
    ctrl = EmployeeController(EmployeeRepository(db_session), auth)

    mgmt = seeded_staff["mgmt"]
    target = seeded_staff["support"]

    updated = ctrl.update_employee(
        user_data={"id": mgmt.id, "department": "MANAGEMENT"},
        emp_id=target.id,
        update_data={"password": "new_password"},
    )

    assert updated is not None
    assert updated.password != "new_password"
    # check password not seen
    assert updated.password != "new_password"

    # check Argon2 format
    assert updated.password.startswith("$argon2")


def test_event_controller_update_denied_when_not_assigned_support(
    db_session, seeded_business, seeded_staff, capsys
):
    auth = DummyAuthController(allowed={"update_event"})
    ctrl = EventController(EventRepository(db_session), auth)

    event = seeded_business["event"]
    other_support = seeded_staff["mgmt"]  # not assigned, not SUPPORT, not MANAGEMENT?

    out = ctrl.update_event(
        user_data={"id": other_support.id, "department": "SALES"},
        event_id=event.id,
        updates={"notes": "hack"},
    )
    captured = capsys.readouterr().out

    assert out is None
    assert "access denied" in captured.lower() or "denied" in captured.lower()