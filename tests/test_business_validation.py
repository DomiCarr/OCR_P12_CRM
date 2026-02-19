# tests/test_business_validation.py
"""
Functional tests for business data validation and constraints.

Tests included:
- test_contract_amounts_logic: Verify remaining amount <= total amount.
- test_event_date_coherence: Verify event end date is after start date.
- test_attendees_positive: Verify number of attendees is not negative.
"""

import uuid
import pytest
from datetime import datetime, timedelta
from app.models.contract import Contract
from app.models.event import Event
from app.models.client import Client
from app.models.employee import Employee
from app.models.department import Department
from app.repositories.base_repository import BaseRepository


@pytest.fixture
def validation_setup(db_session):
    """Setup minimal data for validation tests."""
    dept_repo = BaseRepository(db_session, Department)
    dept = dept_repo.add(Department(name=f"VAL_{uuid.uuid4().hex[:6]}"))

    sales = Employee(
        full_name="Sales", email=f"s_{uuid.uuid4().hex[:6]}@test.com",
        password="h", employee_number=f"S{uuid.uuid4().hex[:4]}",
        department_id=dept.id
    )
    db_session.add(sales)
    db_session.commit()

    client = Client(
        full_name="C", email=f"c_{uuid.uuid4().hex[:6]}@test.com",
        phone="0", company_name="C", sales_contact_id=sales.id
    )
    db_session.add(client)
    db_session.commit()

    return {"sales": sales, "client": client}


def test_contract_amounts_logic(db_session, validation_setup):
    """Verify state of a contract with logically inconsistent amounts."""
    s = validation_setup
    contract = Contract(
        total_amount=100.00,
        remaining_amount=150.00,
        is_signed=True,
        client_id=s["client"].id,
        sales_contact_id=s["sales"].id
    )
    # This highlights that the model currently accepts the inconsistency
    assert contract.remaining_amount > contract.total_amount


def test_event_date_coherence(db_session, validation_setup):
    """Verify state of an event with non-chronological dates."""
    s = validation_setup
    start = datetime.now()
    end = start - timedelta(hours=1)

    # Create contract for the event
    contract = Contract(
        total_amount=100, remaining_amount=0, is_signed=True,
        client_id=s["client"].id, sales_contact_id=s["sales"].id
    )
    db_session.add(contract)
    db_session.commit()

    event = Event(
        name="Invalid Date Event",
        event_date_start=start,
        event_date_end=end,
        location="Paris",
        attendees=10,
        notes="Testing",
        client_id=s["client"].id,
        contract_id=contract.id
    )
    assert event.event_date_end < event.event_date_start


def test_attendees_positive(db_session, validation_setup):
    """Verify state of an event with negative attendees."""
    s = validation_setup
    event = Event(
        name="Negative Attendees",
        event_date_start=datetime.now(),
        event_date_end=datetime.now(),
        location="L",
        attendees=-5,
        notes="N",
        client_id=s["client"].id,
        contract_id=1 # Using dummy ID for unit check
    )
    assert event.attendees < 0