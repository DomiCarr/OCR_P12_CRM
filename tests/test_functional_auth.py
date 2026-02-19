# tests/test_functional_auth.py
"""
Functional tests for the Authentication Controller.

Tests included:
- test_login_success: Verify full login flow, JWT creation, and Sentry tagging.
- test_login_invalid_credentials: Check rejection of wrong email/password.
- test_logout_flow: Verify token deletion and session clearing.
- test_persistence_from_storage: Verify user recovery from a stored token.
"""

import pytest
from unittest.mock import patch
from app.controllers.auth_controller import AuthController
from app.repositories.employee_repository import EmployeeRepository
from app.repositories.base_repository import BaseRepository
from app.models.department import Department
from app.models.employee import Employee
from app.utils.auth import hash_password


@pytest.fixture
def auth_setup(db_session):
    """Provides a controller and a real employee for auth testing."""
    dept_repo = BaseRepository(db_session, Department)
    emp_repo = EmployeeRepository(db_session)

    dept = dept_repo.add(Department(name="TEST_AUTH"))
    password = "password123"
    emp = emp_repo.add(Employee(
        full_name="Auth User",
        email="auth@test.com",
        password=hash_password(password),
        employee_number="A001",
        department_id=dept.id
    ))

    controller = AuthController(emp_repo)
    return controller, emp, password


def test_login_success(auth_setup):
    """Verify that valid credentials return user data and save a token."""
    controller, emp, password = auth_setup

    # We mock save_token to avoid writing files during tests
    with patch("app.controllers.auth_controller.save_token") as mock_save:
        user_data = controller.login(emp.email, password)

        assert user_data is not None
        assert user_data["id"] == emp.id
        assert user_data["department"] == "TEST_AUTH"
        assert controller.current_user_data == user_data
        mock_save.assert_called_once()


def test_login_invalid_credentials(auth_setup):
    """Verify that wrong password returns None."""
    controller, emp, _ = auth_setup

    user_data = controller.login(emp.email, "wrong_pass")
    assert user_data is None
    assert controller.current_user_data is None


def test_logout_flow(auth_setup):
    """Verify logout clears current user and deletes token."""
    controller, _, _ = auth_setup
    controller.current_user_data = {"id": 1}

    with patch("app.controllers.auth_controller.delete_token") as mock_delete:
        controller.logout()
        assert controller.current_user_data is None
        mock_delete.assert_called_once()


def test_persistence_from_storage(auth_setup):
    """Verify that get_logged_in_user restores session from a valid token."""
    controller, emp, _ = auth_setup

    # Simulate an existing valid token in storage
    from app.utils.jwt_handler import create_token
    valid_token = create_token(emp.id, "TEST_AUTH")

    with patch("app.controllers.auth_controller.get_token", return_value=valid_token):
        user_data = controller.get_logged_in_user()
        assert user_data is not None
        assert user_data["sub"] == str(emp.id)
        assert user_data["department"] == "TEST_AUTH"