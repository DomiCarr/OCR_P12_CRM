# tests/test_models_business.py
"""
Unit tests for Business models (Client, Contract, and Event).

Tests included:
- test_create_client: Verify client creation and relationship with sales.
- test_create_contract: Verify contract linked to client and sales contact.
- test_create_event: Verify event linked to contract, client and support.
- test_client_email_uniqueness: Ensure client emails are unique.
"""

import uuid
from datetime import datetime, timedelta
import pytest
from sqlalchemy.exc import IntegrityError
from app.models.department import Department
from app.models.employee import Employee
from app.models.client import Client
from app.models.contract import Contract
from app.models.event import Event


@pytest.fixture
def test_setup(db_session):
    """Fixture to provide a department and employees for business tests."""
    dept_sales = Department(name=f"SALES_{uuid.uuid4().hex[:6]}")
    dept_support = Department(name=f"SUPPORT_{uuid.uuid4().hex[:6]}")
    db_session.add_all([dept_sales, dept_support])
    db_session.commit()

    sales = Employee(
        full_name="Sales Guy",
        email=f"sales_{uuid.uuid4().hex[:6]}@epic.com",
        password="hash",
        employee_number=f"S_{uuid.uuid4().hex[:6]}",
        department_id=dept_sales.id
    )
    support = Employee(
        full_name="Support Guy",
        email=f"support_{uuid.uuid4().hex[:6]}@epic.com",
        password="hash",
        employee_number=f"SUP_{uuid.uuid4().hex[:6]}",
        department_id=dept_support.id
    )
    db_session.add_all([sales, support])
    db_session.commit()
    return sales, support


def test_create_client(db_session, test_setup):
    """Test client creation linked to a sales employee."""
    sales, _ = test_setup
    unique_email = f"client_{uuid.uuid4().hex[:6]}@corp.com"
    client = Client(
        full_name="Alice Client",
        email=unique_email,
        phone="0123456789",
        company_name="Alice Corp",
        sales_contact_id=sales.id
    )
    db_session.add(client)
    db_session.commit()

    assert client.id is not None
    assert client.sales_contact.full_name == "Sales Guy"
    assert str(client) == "<Client(name=Alice Client, company=Alice Corp)>"


def test_create_contract(db_session, test_setup):
    """Test contract creation with amounts and signature status."""
    sales, _ = test_setup
    client = Client(
        full_name="Contract Client",
        email=f"c_{uuid.uuid4().hex[:6]}@test.com",
        phone="000",
        company_name="C-Corp",
        sales_contact_id=sales.id
    )
    db_session.add(client)
    db_session.commit()

    contract = Contract(
        total_amount=1000.50,
        remaining_amount=500.00,
        is_signed=True,
        client_id=client.id,
        sales_contact_id=sales.id
    )
    db_session.add(contract)
    db_session.commit()

    assert contract.id is not None
    assert float(contract.total_amount) == 1000.50
    assert contract.client.full_name == "Contract Client"


def test_create_event(db_session, test_setup):
    """Test full event chain link: Client -> Contract -> Event."""
    sales, support = test_setup
    client = Client(
        full_name="Event Client",
        email=f"e_{uuid.uuid4().hex[:6]}@event.com",
        phone="111",
        company_name="E-Events",
        sales_contact_id=sales.id
    )
    db_session.add(client)
    db_session.commit()

    contract = Contract(
        total_amount=5000,
        remaining_amount=0,
        is_signed=True,
        client_id=client.id,
        sales_contact_id=sales.id
    )
    db_session.add(contract)
    db_session.commit()

    start_date = datetime.now() + timedelta(days=7)
    event = Event(
        name="Epic Party",
        event_date_start=start_date,
        event_date_end=start_date + timedelta(hours=5),
        location="Paris",
        attendees=100,
        notes="Important event",
        client_id=client.id,
        contract_id=contract.id,
        support_contact_id=support.id
    )
    db_session.add(event)
    db_session.commit()

    assert event.id is not None
    assert event.contract.is_signed is True
    assert event.support_contact.full_name == "Support Guy"


def test_client_email_uniqueness(db_session, test_setup):
    """Verify that two clients cannot share the same email."""
    sales, _ = test_setup
    email = "duplicate@test.com"
    c1 = Client(
        full_name="C1", email=email, phone="1",
        company_name="A", sales_contact_id=sales.id
    )
    db_session.add(c1)
    db_session.commit()

    c2 = Client(
        full_name="C2", email=email, phone="2",
        company_name="B", sales_contact_id=sales.id
    )
    db_session.add(c2)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()