# tests/test_functional_sales.py
"""
Functional tests for Sales (T13) operations.

Tests included:
- test_sales_can_create_client: Verify creation and auto-assignment.
- test_support_cannot_create_client: Verify permission restriction.
- test_sales_can_update_own_client: Success for assigned contact.
- test_sales_cannot_update_other_client: Denied for non-assigned contact.
"""

import uuid
import pytest
from sqlalchemy import select
from app.controllers.client_controller import ClientController
from app.controllers.auth_controller import AuthController
from app.repositories.client_repository import ClientRepository
from app.repositories.employee_repository import EmployeeRepository
from app.models.department import Department
from app.models.employee import Employee
from app.repositories.base_repository import BaseRepository


@pytest.fixture
def sales_suite(db_session):
    """Setup repositories and controllers for sales tests."""
    dept_repo = BaseRepository(db_session, Department)
    emp_repo = EmployeeRepository(db_session)
    client_repo = ClientRepository(db_session)
    auth_ctrl = AuthController(emp_repo)
    client_ctrl = ClientController(client_repo, auth_ctrl)

    sales_dept = db_session.execute(
        select(Department).filter_by(name="SALES")
    ).scalar_one_or_none()
    if not sales_dept:
        sales_dept = dept_repo.add(Department(name="SALES"))

    # Create two different sales employees
    unique_1 = uuid.uuid4().hex[:6]
    sales_1 = emp_repo.add(Employee(
        full_name="Sales One", email=f"s1_{unique_1}@crm.com",
        password="p", employee_number=f"S1_{unique_1}",
        department_id=sales_dept.id
    ))

    unique_2 = uuid.uuid4().hex[:6]
    sales_2 = emp_repo.add(Employee(
        full_name="Sales Two", email=f"s2_{unique_2}@crm.com",
        password="p", employee_number=f"S2_{unique_2}",
        department_id=sales_dept.id
    ))

    return {
        "client_ctrl": client_ctrl,
        "sales_1": sales_1,
        "sales_2": sales_2
    }


def test_sales_can_create_client(sales_suite):
    """Verify that a SALES user can create a client with auto-assignment."""
    ctrl = sales_suite["client_ctrl"]
    user = sales_suite["sales_1"]
    user_data = {"id": user.id, "department": "SALES"}
    client_data = {
        "full_name": "Test Client Inc",
        "email": f"contact_{uuid.uuid4().hex[:6]}@client.com",
        "phone": "0102030405", "company_name": "Test Corp"
    }
    new_client = ctrl.create_client(user_data=user_data, client_data=client_data)
    assert new_client is not None
    assert new_client.sales_contact_id == user.id


def test_support_cannot_create_client(sales_suite):
    """Verify that a SUPPORT user cannot create a client."""
    ctrl = sales_suite["client_ctrl"]
    user_data = {"id": 999, "department": "SUPPORT"}
    client_data = {
        "full_name": "Forbidden", "email": "f@client.com",
        "phone": "0000", "company_name": "No Access"
    }
    result = ctrl.create_client(user_data=user_data, client_data=client_data)
    assert result is None


def test_sales_can_update_own_client(sales_suite):
    """Verify sales can update their assigned client."""
    ctrl = sales_suite["client_ctrl"]
    s1 = sales_suite["sales_1"]
    user_data = {"id": s1.id, "department": "SALES"}

    # Create client first
    client_data = {
        "full_name": "Owned Client", "email": f"c_{uuid.uuid4().hex[:4]}@c.com",
        "phone": "123", "company_name": "Own", "sales_contact_id": s1.id
    }
    client = ctrl.create_client(user_data=user_data, client_data=client_data)

    updated = ctrl.update_client(user_data=user_data, client_id=client.id, updates={"phone": "999"})
    assert updated is not None
    assert updated.phone == "999"


def test_sales_cannot_update_other_client(sales_suite):
    """Verify sales cannot update a client assigned to someone else."""
    ctrl = sales_suite["client_ctrl"]
    s1 = sales_suite["sales_1"]
    s2 = sales_suite["sales_2"]

    # Client belongs to s1
    client_data = {
        "full_name": "S1 Client", "email": f"c_{uuid.uuid4().hex[:4]}@c.com",
        "phone": "123", "company_name": "S1 Corp", "sales_contact_id": s1.id
    }
    client = ctrl.create_client(user_data={"id": s1.id, "department": "SALES"}, client_data=client_data)

    # S2 tries to update S1's client
    result = ctrl.update_client(user_data={"id": s2.id, "department": "SALES"},
                                client_id=client.id, updates={"phone": "000"})
    assert result is None