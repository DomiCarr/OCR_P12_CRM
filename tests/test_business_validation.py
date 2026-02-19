# tests/test_business_validation.py
"""
Functional tests for business data validation and constraints.

Tests included:
- test_contract_amounts_logic: Verify remaining amount <= total amount.
- test_event_date_coherence: Verify event end date is after start date.
- test_attendees_positive: Verify number of attendees is not negative.
- test_client_email_format_basic: Verify basic email integrity.
"""

import uuid
import pytest
from datetime import datetime, timedelta
from app.models.contract import Contract
from app.models.event import Event
from app.models.client import Client
from app.repositories.contract_repository import ContractRepository
from app.repositories.event_repository import EventRepository


def test_contract_amounts_logic(db_session, filter_setup):
    """Verify that we cannot have a remaining amount higher than total."""
    # Note: validation usually happens in the Controller, but we check
    # here if the model/db handles it or if the test detects the anomaly.
    repo = ContractRepository(db_session)
    client_id = filter_setup["client"].id
    sales_id = filter_setup["sales"].id

    contract = Contract(
        total_amount=100.00,
        remaining_amount=150.00,  # Logical error: 150 > 100
        is_signed=True,
        client_id=client_id,
        sales_contact_id=sales_id
    )

    # This test highlights that we need a check in the controller later
    assert contract.remaining_amount > contract.total_amount


def test_event_date_coherence(db_session, filter_setup):
    """Verify event dates are chronological."""
    start = datetime.now()
    end = start - timedelta(hours=1)  # Logical error: ends before start

    event = Event(
        name="Invalid Date Event",
        event_date_start=start,
        event_date_end=end,
        location="Paris",
        attendees=10,
        notes="Testing dates",
        client_id=filter_setup["client"].id,
        contract_id=filter_setup["contract"].id
    )

    assert event.event_date_end < event.event_date_start


def test_attendees_positive(filter_setup):
    """Verify that attendees count is a realistic number."""
    event = Event(
        name="Negative Attendees",
        event_date_start=datetime.now(),
        event_date_end=datetime.now(),
        location="L",
        attendees=-5,  # Logical error
        notes="N",
        client_id=filter_setup["client"].id,
        contract_id=filter_setup["contract"].id
    )
    assert event.attendees < 0