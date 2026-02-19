# tests/test_logic_filters.py
"""
Unit tests for specialized repository filtering logic.

Tests included:
- test_filter_unpaid_contracts: Verify only contracts with remaining_amount > 0 are returned.
- test_filter_events_without_support: Verify events with support_contact_id=None are returned.
- test_filter_unsigned_contracts: Verify only is_signed=False contracts are returned.
- test_filter_my_events: Verify support agents only see their assigned events.
"""

import uuid
import pytest
from datetime import datetime
from app.repositories.contract_repository import ContractRepository
from app.repositories.event_repository import EventRepository
from app.repositories.client_repository import ClientRepository
from app.repositories.employee_repository import EmployeeRepository
from app.repositories.base_repository import BaseRepository
from app.models.department import Department
from app.models.employee import Employee
from app.models.client import Client
from app.models.contract import Contract
from app.models.event import Event


@pytest.fixture
def filter_setup(db_session):
    """Setup a batch of data with various states for filtering tests."""
    dept_repo = BaseRepository(db_session, Department)
    emp_repo = EmployeeRepository(db_session)
    client_repo = ClientRepository(db_session)
    contract_repo = ContractRepository(db_session)

    dept = dept_repo.add(Department(name=f"FILT_{uuid.uuid4().hex[:6]}"))
    sales = emp_repo.add(Employee(
        full_name="Sales",
        email=f"s_{uuid.uuid4().hex[:6]}@test.com",
        password="h",
        employee_number=f"S{uuid.uuid4().hex[:4]}",
        department_id=dept.id
    ))
    support = emp_repo.add(Employee(
        full_name="Support",
        email=f"p_{uuid.uuid4().hex[:6]}@test.com",
        password="h",
        employee_number=f"P{uuid.uuid4().hex[:4]}",
        department_id=dept.id
    ))
    client = client_repo.add(Client(
        full_name="C",
        email=f"c_{uuid.uuid4().hex[:6]}@test.com",
        phone="0",
        company_name="C",
        sales_contact_id=sales.id
    ))
    # Create default contract for events
    contract = contract_repo.add(Contract(
        total_amount=1000,
        remaining_amount=500,
        is_signed=True,
        client_id=client.id,
        sales_contact_id=sales.id
    ))

    return {
        "db": db_session,
        "sales": sales,
        "support": support,
        "client": client,
        "contract": contract,
        "contract_repo": contract_repo,
        "event_repo": EventRepository(db_session)
    }


def test_filter_unpaid_contracts(filter_setup):
    """Verify that only contracts with a remaining balance are fetched."""
    repo = filter_setup["contract_repo"]
    client_id = filter_setup["client"].id
    sales_id = filter_setup["sales"].id

    repo.add(Contract(
        total_amount=1000, remaining_amount=0, is_signed=True,
        client_id=client_id, sales_contact_id=sales_id
    ))
    repo.add(Contract(
        total_amount=1000, remaining_amount=500, is_signed=True,
        client_id=client_id, sales_contact_id=sales_id
    ))

    unpaid = repo.get_unpaid_contracts()
    assert all(c.remaining_amount > 0 for c in unpaid)


def test_filter_events_without_support(filter_setup):
    """Verify that we can find events that need a support assignment."""
    repo = filter_setup["event_repo"]
    client_id = filter_setup["client"].id
    contract_id = filter_setup["contract"].id

    # Event with support
    repo.add(Event(
        name="E1", event_date_start=datetime.now(),
        event_date_end=datetime.now(), location="L", attendees=10,
        notes="N", client_id=client_id, contract_id=contract_id,
        support_contact_id=filter_setup["support"].id
    ))
    # Event without support
    repo.add(Event(
        name="E2", event_date_start=datetime.now(),
        event_date_end=datetime.now(), location="L", attendees=10,
        notes="N", client_id=client_id, contract_id=contract_id,
        support_contact_id=None
    ))

    no_support = repo.get_events_without_support()
    assert any(e.name == "E2" for e in no_support)
    assert all(e.support_contact_id is None for e in no_support)


def test_filter_unsigned_contracts(filter_setup):
    """Verify filtering of unsigned contracts."""
    repo = filter_setup["contract_repo"]
    client_id = filter_setup["client"].id
    sales_id = filter_setup["sales"].id

    repo.add(Contract(
        total_amount=100, remaining_amount=100, is_signed=False,
        client_id=client_id, sales_contact_id=sales_id
    ))

    unsigned = repo.get_unsigned_contracts()
    assert any(c.is_signed is False for c in unsigned)


def test_filter_my_events(filter_setup):
    """Verify support agents only see their assigned events."""
    repo = filter_setup["event_repo"]
    client_id = filter_setup["client"].id
    contract_id = filter_setup["contract"].id
    support_id = filter_setup["support"].id

    repo.add(Event(
        name="My Event", event_date_start=datetime.now(),
        event_date_end=datetime.now(), location="L", attendees=5,
        notes="N", client_id=client_id, contract_id=contract_id,
        support_contact_id=support_id
    ))

    my_events = repo.get_my_events(support_id)
    assert all(e.support_contact_id == support_id for e in my_events)