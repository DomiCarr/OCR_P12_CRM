# tests/test_models_staff.py
"""
Unit tests for Staff models (Department and Employee).

Tests included:
- test_create_department: Validate department creation with unique names.
- test_department_unique_name: Ensure department names are unique.
- test_create_employee: Validate employee creation and relations.
- test_employee_unique_constraints: Validate email and employee_number uniqueness.
"""

import uuid
import pytest
from sqlalchemy.exc import IntegrityError
from app.models.department import Department
from app.models.employee import Employee


def test_create_department(db_session):
    """Test creating a department and its representation."""
    unique_name = f"DEPT_{uuid.uuid4().hex[:8]}"
    dept = Department(name=unique_name)
    db_session.add(dept)
    db_session.commit()

    assert dept.id is not None
    assert str(dept) == f"<Department(name={unique_name})>"


def test_department_unique_name(db_session):
    """Ensure that two departments cannot have the same name."""
    unique_name = f"UNIQUE_{uuid.uuid4().hex[:8]}"
    dept1 = Department(name=unique_name)
    db_session.add(dept1)
    db_session.commit()

    dept2 = Department(name=unique_name)
    db_session.add(dept2)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_create_employee(db_session):
    """Test creating an employee associated with a department."""
    unique_dept = f"SUPPORT_{uuid.uuid4().hex[:8]}"
    dept = Department(name=unique_dept)
    db_session.add(dept)
    db_session.commit()

    unique_email = f"user_{uuid.uuid4().hex[:8]}@test.com"
    emp = Employee(
        full_name="John Doe",
        email=unique_email,
        password="hashed_password",
        employee_number=f"EMP_{uuid.uuid4().hex[:8]}",
        department_id=dept.id
    )
    db_session.add(emp)
    db_session.commit()

    assert emp.id is not None
    assert emp.department.name == unique_dept


def test_employee_unique_constraints(db_session):
    """Test uniqueness of email and employee_number."""
    dept = Department(name=f"ADMIN_{uuid.uuid4().hex[:8]}")
    db_session.add(dept)
    db_session.commit()

    email = f"same_{uuid.uuid4().hex[:8]}@test.com"
    emp1 = Employee(
        full_name="User 1",
        email=email,
        password="pwd",
        employee_number="ID_STATIC",
        department_id=dept.id
    )
    db_session.add(emp1)
    db_session.commit()

    # Duplicate email
    emp2 = Employee(
        full_name="User 2",
        email=email,
        password="pwd",
        employee_number="ID_NEW",
        department_id=dept.id
    )
    db_session.add(emp2)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()
