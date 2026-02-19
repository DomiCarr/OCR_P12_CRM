# tests/test_models_staff.py
"""
Unit tests for Staff models (Department and Employee).

Tests included:
- test_create_department: Validate department creation and naming.
- test_department_unique_name: Ensure department names are unique.
- test_create_employee: Validate employee creation and relations.
- test_employee_unique_constraints: Validate email and employee_number uniqueness.
"""

import pytest
from sqlalchemy.exc import IntegrityError
from app.models.department import Department
from app.models.employee import Employee


def test_create_department(db_session):
    """Test creating a department and its representation."""
    dept = Department(name="MANAGEMENT")
    db_session.add(dept)
    db_session.commit()

    assert dept.id is not None
    assert str(dept) == "<Department(name=MANAGEMENT)>"


def test_department_unique_name(db_session):
    """Ensure that two departments cannot have the same name."""
    dept1 = Department(name="SALES")
    db_session.add(dept1)
    db_session.commit()

    dept2 = Department(name="SALES")
    db_session.add(dept2)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_create_employee(db_session):
    """Test creating an employee associated with a department."""
    dept = Department(name="SUPPORT")
    db_session.add(dept)
    db_session.commit()

    emp = Employee(
        full_name="John Doe",
        email="john.doe@epicevents.com",
        password="hashed_password",
        employee_number="EMP001",
        department_id=dept.id
    )
    db_session.add(emp)
    db_session.commit()

    assert emp.id is not None
    assert emp.department.name == "SUPPORT"
    assert "John Doe" in str(emp)


def test_employee_unique_constraints(db_session):
    """Test uniqueness of email and employee_number."""
    dept = Department(name="ADMIN")
    db_session.add(dept)
    db_session.commit()

    emp1 = Employee(
        full_name="User 1",
        email="unique@test.com",
        password="pwd",
        employee_number="ID001",
        department_id=dept.id
    )
    db_session.add(emp1)
    db_session.commit()

    # Duplicate email
    emp2 = Employee(
        full_name="User 2",
        email="unique@test.com",
        password="pwd",
        employee_number="ID002",
        department_id=dept.id
    )
    db_session.add(emp2)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()