# tests/test_repositories.py
"""
Unit tests for Repositories.

Tests included:
- test_employee_repo_get_by_email: Verify lookup by email.
- test_employee_repo_add: Verify adding an employee via repo.
- test_repo_rollback_on_error: Ensure BaseRepository rolls back on failure.
"""

import uuid
import pytest
from sqlalchemy.exc import IntegrityError
from app.models.employee import Employee
from app.models.department import Department
from app.repositories.employee_repository import EmployeeRepository


@pytest.fixture
def employee_repo(db_session):
    """Fixture to provide the employee repository."""
    return EmployeeRepository(db_session)


def test_employee_repo_add(employee_repo, db_session):
    """Test adding an employee using the repository method."""
    # Setup department
    dept = Department(name=f"TECH_{uuid.uuid4().hex[:6]}")
    db_session.add(dept)
    db_session.commit()

    emp = Employee(
        full_name="Test Repo",
        email=f"repo_{uuid.uuid4().hex[:6]}@test.com",
        password="hash",
        employee_number=f"ID_{uuid.uuid4().hex[:6]}",
        department_id=dept.id
    )

    # Action via le repository
    employee_repo.add(emp)

    # Verification
    fetched = employee_repo.get_by_id(emp.id)
    assert fetched is not None
    assert fetched.full_name == "Test Repo"


def test_employee_repo_get_by_email(employee_repo, db_session):
    """Test finding an employee by email via the repository."""
    dept = Department(name=f"HR_{uuid.uuid4().hex[:6]}")
    db_session.add(dept)
    db_session.commit()

    email = f"findme_{uuid.uuid4().hex[:6]}@test.com"
    emp = Employee(
        full_name="Search Target",
        email=email,
        password="hash",
        employee_number=f"SN_{uuid.uuid4().hex[:6]}",
        department_id=dept.id
    )
    employee_repo.add(emp)

    found = employee_repo.get_by_email(email)
    assert found is not None
    assert found.id == emp.id


def test_repo_rollback_on_error(employee_repo, db_session):
    """Verify that BaseRepository handles IntegrityError and rolls back."""
    dept = Department(name=f"VOID_{uuid.uuid4().hex[:6]}")
    db_session.add(dept)
    db_session.commit()

    email = "duplicate@test.com"
    emp1 = Employee(
        full_name="User 1", email=email, password="h",
        employee_number="N1", department_id=dept.id
    )
    employee_repo.add(emp1)

    emp2 = Employee(
        full_name="User 2", email=email, password="h",
        employee_number="N2", department_id=dept.id
    )

    # Le BaseRepository doit lever l'erreur et faire le rollback
    with pytest.raises(IntegrityError):
        employee_repo.add(emp2)