# tests/test_integration_staff_repos.py
"""
Integration tests for Staff Repositories (Department & Employee).

Tests included:
- test_staff_creation_flow: Create a department then an employee linked to it.
- test_employee_unique_constraints_repo: Verify IntegrityError via Repository.
- test_department_lookup: Verify fetching department by name.
"""

import uuid
import pytest
from sqlalchemy.exc import IntegrityError
from app.repositories.department_repository import DepartmentRepository
from app.repositories.employee_repository import EmployeeRepository
from app.models.department import Department
from app.models.employee import Employee


@pytest.fixture
def staff_repos(db_session):
    """Fixture providing both staff repositories."""
    return DepartmentRepository(db_session), EmployeeRepository(db_session)


def test_staff_creation_flow(staff_repos):
    """Test full integration: creating a department and a linked employee."""
    dept_repo, emp_repo = staff_repos

    # 1. Create Department
    dept_name = f"DEPT_{uuid.uuid4().hex[:6]}"
    dept = Department(name=dept_name)
    dept_repo.add(dept)

    # 2. Create Employee linked to Dept
    emp_email = f"staff_{uuid.uuid4().hex[:6]}@epic.com"
    emp = Employee(
        full_name="Staff Member",
        email=emp_email,
        password="secure_hash",
        employee_number=f"EMP_{uuid.uuid4().hex[:6]}",
        department_id=dept.id
    )
    emp_repo.add(emp)

    # 3. Verify Integration
    fetched_emp = emp_repo.get_by_email(emp_email)
    assert fetched_emp.department.name == dept_name


def test_employee_unique_constraints_repo(staff_repos):
    """Verify that repositories correctly handle DB unique constraints."""
    dept_repo, emp_repo = staff_repos

    dept = Department(name=f"UNIQUE_DEPT_{uuid.uuid4().hex[:6]}")
    dept_repo.add(dept)

    shared_email = "duplicate@epic.com"
    emp1 = Employee(
        full_name="User 1", email=shared_email, password="h",
        employee_number="N1", department_id=dept.id
    )
    emp_repo.add(emp1)

    emp2 = Employee(
        full_name="User 2", email=shared_email, password="h",
        employee_number="N2", department_id=dept.id
    )

    with pytest.raises(IntegrityError):
        emp_repo.add(emp2)


def test_department_lookup(staff_repos):
    """Test the specific get_by_name method in DepartmentRepository."""
    dept_repo, _ = staff_repos
    name = "SUPPORT_TEAM"
    dept = Department(name=name)
    dept_repo.add(dept)

    found = dept_repo.get_by_name(name)
    assert found is not None
    assert found.id == dept.id