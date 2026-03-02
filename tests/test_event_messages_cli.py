# tests/test_event_messages_cli.py

from __future__ import annotations

from datetime import datetime, timedelta
import uuid

import pytest

from app.controllers.event_controller import EventController
from app.models.client import Client
from app.models.contract import Contract
from app.models.department import Department
from app.models.employee import Employee
from app.models.event import Event
from app.repositories.event_repository import EventRepository


class DummyAuthController:
    """Minimal auth controller to drive controller permission branches."""
    def __init__(self, allowed: set[str]):
        self.allowed = allowed
        self.current_user_data: dict | None = None

    def check_user_permission(self, permission: str) -> bool:
        return permission in self.allowed


@pytest.fixture
def seeded_context(db_session):
    """
    Create a minimal dataset:
    - departments + employees (sales/support/mgmt)
    - one client owned by sales
    - one signed contract + one unsigned contract
    - one event assigned to support (for update tests)
    """
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
    db_session.flush()

    client = Client(
        full_name="Client Seed",
        email=f"client_{uuid.uuid4().hex[:6]}@t.com",
        phone="0102030405",
        company_name="Corp",
        sales_contact_id=sales.id,
    )
    db_session.add(client)
    db_session.flush()

    unsigned_contract = Contract(
        total_amount=100.0,
        remaining_amount=100.0,
        is_signed=False,
        client_id=client.id,
        sales_contact_id=sales.id,
    )
    signed_contract = Contract(
        total_amount=100.0,
        remaining_amount=20.0,
        is_signed=True,
        client_id=client.id,
        sales_contact_id=sales.id,
    )
    db_session.add_all([unsigned_contract, signed_contract])
    db_session.flush()

    event = Event(
        name="Seed Event",
        event_date_start=datetime.now() + timedelta(days=1),
        event_date_end=datetime.now() + timedelta(days=2),
        location="Paris",
        attendees=10,
        notes="seed",
        client_id=client.id,
        contract_id=signed_contract.id,
        support_contact_id=support.id,
    )
    db_session.add(event)
    db_session.commit()

    return {
        "sales": sales,
        "support": support,
        "mgmt": mgmt,
        "client": client,
        "unsigned_contract": unsigned_contract,
        "signed_contract": signed_contract,
        "event": event,
    }


def test_create_event_unsigned_contract_prints_reason(db_session, seeded_context, capfd):
    auth = DummyAuthController(allowed={"create_event"})
    ctrl = EventController(EventRepository(db_session), auth)

    contract = seeded_context["unsigned_contract"]
    sales = seeded_context["sales"]

    out = ctrl.create_event(
        user_data={"id": sales.id, "department": "SALES"},
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

    printed = capfd.readouterr().out.lower()
    # Be tolerant to message variations
    assert "unsigned" in printed or "not signed" in printed


def test_create_event_not_owner_prints_reason(db_session, seeded_context, capfd):
    auth = DummyAuthController(allowed={"create_event"})
    ctrl = EventController(EventRepository(db_session), auth)

    contract = seeded_context["signed_contract"]
    not_owner = seeded_context["support"]  # not the sales contact

    out = ctrl.create_event(
        user_data={"id": not_owner.id, "department": "SUPPORT"},
        event_data={
            "name": "Denied Not Owner",
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

    printed = capfd.readouterr().out.lower()
    assert "sales contact" in printed or "not the sales" in printed


def test_update_event_not_found_prints_message(db_session, seeded_context, capfd):
    auth = DummyAuthController(allowed={"update_event"})
    ctrl = EventController(EventRepository(db_session), auth)

    out = ctrl.update_event(
        user_data={"id": seeded_context["mgmt"].id, "department": "MANAGEMENT"},
        event_id=999999,
        updates={"notes": "x"},
    )
    assert out is None

    printed = capfd.readouterr().out.lower()
    assert "not found" in printed


def test_update_event_denied_when_not_assigned_prints_message(db_session, seeded_context, capfd):
    auth = DummyAuthController(allowed={"update_event"})
    ctrl = EventController(EventRepository(db_session), auth)

    event = seeded_context["event"]
    not_assigned = seeded_context["sales"]  # event is assigned to support

    out = ctrl.update_event(
        user_data={"id": not_assigned.id, "department": "SALES"},
        event_id=event.id,
        updates={"notes": "x"},
    )
    assert out is None

    printed = capfd.readouterr().out.lower()
    assert "access denied" in printed
    assert "assigned support" in printed or "support contact" in printed


def test_get_events_without_support_filters_correctly(db_session, seeded_context):
    repo = EventRepository(db_session)

    # Existing event has support_contact_id set (seeded_context["support"].id)
    # Add another event without support_contact_id
    contract = seeded_context["signed_contract"]
    e2 = Event(
        name="No Support",
        event_date_start=datetime.now() + timedelta(days=3),
        event_date_end=datetime.now() + timedelta(days=4),
        location="Lyon",
        attendees=5,
        notes="n",
        client_id=contract.client_id,
        contract_id=contract.id,
        support_contact_id=None,
    )
    repo.add(e2)

    no_support = repo.get_events_without_support()
    assert any(e.name == "No Support" for e in no_support)
    assert all(e.support_contact_id is None for e in no_support)