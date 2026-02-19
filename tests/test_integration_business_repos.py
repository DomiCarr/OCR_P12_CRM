# tests/test_integration_business_repos.py
"""
Integration tests for Business Repositories (Client, Contract, Event).

Tests included:
- test_client_contract_event_chain: Verify the full creation chain with FKs.
- test_contract_integrity_violation: Verify error when client is missing.
- test_event_logic_queries: Verify business filters (unsigned, unpaid, etc.).
"""

import uuid
import pytest
from sqlalchemy.exc import IntegrityError
from app.repositories.client_repository import ClientRepository
from app.repositories.contract_repository import ContractRepository
from app.repositories.event_repository import EventRepository
from app.repositories.employee_repository import EmployeeRepository
from app.repositories.base_repository import BaseRepository
from app.models.department import Department
from app.models.employee import Employee
from app.models.client import Client
from app.models.contract import Contract
from app.models.event import Event
from datetime import datetime, timedelta


@pytest.fixture
def business_setup(db_session):
    """Fixture to provide staff and repositories for business integration."""
    dept_repo = BaseRepository(db_session, Department)
    emp_repo = EmployeeRepository(db_session)

    dept = dept_repo.add(Department(name=f"BIZ_{uuid.uuid4().hex[:6]}"))
    sales = emp_repo.add(Employee(
        full_name="Sales Rep",
        email=f"sales_{uuid.uuid4().hex[:6]}@epic.com",
        password="hash",
        employee_number=f"S_{uuid.uuid4().hex[:6]}",
        department_id=dept.id
    ))

    return {
        "sales": sales,
        "client_repo": ClientRepository(db_session),
        "contract_repo": ContractRepository(db_session),
        "event_repo": EventRepository(db_session)
    }


def test_client_contract_event_chain(business_setup):
    """Test the creation chain: Client -> Contract -> Event."""
    s = business_setup

    # 1. Create Client
    client = s["client_repo"].add(Client(
        full_name="Biz Client",
        email=f"biz_{uuid.uuid4().hex[:6]}@corp.com",
        phone="010203",
        company_name="BizCorp",
        sales_contact_id=s["sales"].id
    ))

    # 2. Create Contract
    contract = s["contract_repo"].add(Contract(
        total_amount=2000.0,
        remaining_amount=1000.0,
        is_signed=True,
        client_id=client.id,
        sales_contact_id=s["sales"].id
    ))

    # 3. Create Event
    event = s["event_repo"].add(Event(
        name="Biz Event",
        event_date_start=datetime.now(),
        event_date_end=datetime.now() + timedelta(hours=2),
        location="Paris",
        attendees=50,
        notes="Notes",
        client_id=client.id,
        contract_id=contract.id
    ))

    assert event.id is not None
    assert event.contract.total_amount == 2000.0
    assert event.client.full_name == "Biz Client"


def test_contract_integrity_violation(business_setup):
    """Verify that a contract cannot be created without a valid client."""
    s = business_setup
    invalid_contract = Contract(
        total_amount=100,
        remaining_amount=100,
        client_id=9999,  # Non-existent
        sales_contact_id=s["sales"].id
    )

    with pytest.raises(IntegrityError):
        s["contract_repo"].add(invalid_contract)


def test_event_logic_queries(business_setup):
    """Verify that specific repository filters return correct data."""
    s = business_setup

    # Create an unsigned contract
    client = s["client_repo"].add(Client(
        full_name="Filter Client",
        email=f"f_{uuid.uuid4().hex[:6]}@test.com",
        phone="0", company_name="F", sales_contact_id=s["sales"].id
    ))

    s["contract_repo"].add(Contract(
        total_amount=500, remaining_amount=500, is_signed=False,
        client_id=client.id, sales_contact_id=s["sales"].id
    ))

    unsigned = s["contract_repo"].get_unsigned_contracts()
    assert len(unsigned) >= 1
    assert any(c.is_signed is False for c in unsigned)