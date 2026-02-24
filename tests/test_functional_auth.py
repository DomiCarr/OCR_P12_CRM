"""
Functional tests for authentication controller flows.

List of tests:
- test_auth_controller_full_flow: Covers logout and failed login logic.
- test_auth_login_success: Covers successful login and user data structure.
"""

import pytest
from app.controllers.auth_controller import AuthController
from app.repositories.employee_repository import EmployeeRepository
from app.models.department import Department
from app.models.employee import Employee
from app.utils.auth import hash_password


@pytest.fixture
def auth_ctrl(db_session):
    """Fixture for AuthController."""
    return AuthController(EmployeeRepository(db_session))


def test_auth_controller_full_flow(auth_ctrl):
    """Covers logout and failed login logic."""
    auth_ctrl.logout()
    assert auth_ctrl.current_user_data is None
    assert auth_ctrl.login("ghost@missing.com", "password") is None
    assert auth_ctrl.check_user_permission("read") is False


def test_auth_login_success(db_session, auth_ctrl):
    """Covers successful login and user data structure."""
    dept = Department(name="AUTH_DEPT")
    db_session.add(dept)
    db_session.flush()

    pwd = hash_password("secret123")
    emp = Employee(
        full_name="Auth Success",
        email="success@test.com",
        password=pwd,
        employee_number="EMP_OK",
        department_id=dept.id
    )
    db_session.add(emp)
    db_session.commit()

    user = auth_ctrl.login("success@test.com", "secret123")
    assert user is not None
    # AuthController.login does not return 'email' in user_data dict
    assert user["full_name"] == "Auth Success"
    assert user["department"] == "AUTH_DEPT"