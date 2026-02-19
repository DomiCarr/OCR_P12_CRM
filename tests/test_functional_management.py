# tests/test_functional_management.py
"""
Functional tests for Management (T12) operations.

Tests included:
- test_list_employees_as_management: Success for authorized users.
- test_create_employee_as_management: Success for authorized users.
- test_create_employee_as_sales_denied: Access control check.
- test_list_contracts_permission: Verify role-based contract access.
"""

import uuid
import pytest
from sqlalchemy import select
from app.controllers.employee_controller import EmployeeController
from app.controllers.contract_controller import ContractController
from app.controllers.auth_controller import AuthController
from app.repositories.employee_repository import EmployeeRepository
from app.repositories.contract_repository import ContractRepository
from app.models.department import Department
from app.repositories.base_repository import BaseRepository


@pytest.fixture
def management_suite(db_session):
    """Setup repositories and controllers with duplicate check."""
    dept_repo = BaseRepository(db_session, Department)
    emp_repo = EmployeeRepository(db_session)
    cont_repo = ContractRepository(db_session)
    auth_ctrl = AuthController(emp_repo)

    existing_dept = db_session.execute(
        select(Department).filter_by(name="MANAGEMENT")
    ).scalar_one_or_none()

    if existing_dept:
        test_dept = existing_dept
    else:
        test_dept = dept_repo.add(Department(name="MANAGEMENT"))

    emp_ctrl = EmployeeController(emp_repo, auth_ctrl)
    cont_ctrl = ContractController(cont_repo, auth_ctrl)

    return {
        "emp_ctrl": emp_ctrl,
        "cont_ctrl": cont_ctrl,
        "dept_id": test_dept.id
    }


def test_list_employees_as_management(management_suite):
    """Verify management can list employees."""
    ctrl = management_suite["emp_ctrl"]
    user_data = {"id": 1, "department": "MANAGEMENT"}

    result = ctrl.list_all_employees(user_data=user_data)
    assert isinstance(result, list)


def test_create_employee_as_management(management_suite):
    """Verify management can create a new employee."""
    ctrl = management_suite["emp_ctrl"]
    user_data = {"id": 1, "department": "MANAGEMENT"}

    email = f"manager_{uuid.uuid4().hex[:6]}@crm.com"
    emp_data = {
        "full_name": "New Manager",
        "email": email,
        "password": "securepassword",
        "employee_number": f"MGT_{uuid.uuid4().hex[:4]}",
        "department_id": management_suite["dept_id"]
    }

    new_emp = ctrl.create_employee(user_data=user_data, employee_data=emp_data)
    assert new_emp is not None
    assert new_emp.email == email


def test_create_employee_as_sales_denied(management_suite):
    """Verify sales role cannot create an employee."""
    ctrl = management_suite["emp_ctrl"]
    user_data = {"id": 2, "department": "SALES"}
    emp_data = {
        "full_name": "Unauthorized",
        "email": f"bad_{uuid.uuid4().hex[:4]}@crm.com",
        "password": "p",
        "employee_number": f"BAD_{uuid.uuid4().hex[:4]}",
        "department_id": management_suite["dept_id"]
    }

    result = ctrl.create_employee(user_data=user_data, employee_data=emp_data)
    assert result is None


def test_list_contracts_permission(management_suite):
    """Verify contract listing access for management."""
    ctrl = management_suite["cont_ctrl"]
    user_data = {"id": 1, "department": "MANAGEMENT"}

    result = ctrl.list_all_contracts(user_data=user_data)
    assert result is not None