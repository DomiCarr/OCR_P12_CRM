# tests/test_functional_permissions.py
"""
Functional tests for Role-Based Access Control (RBAC).

Tests included:
- test_management_can_create_employee: Verify high-level admin rights.
- test_sales_cannot_create_employee: Verify restriction for non-admin roles.
- test_sales_can_create_client: Verify role-specific creation rights.
- test_support_restrictions: Verify support agent cannot create contracts.
"""

import pytest
from app.controllers.auth_controller import AuthController
from app.repositories.employee_repository import EmployeeRepository


@pytest.fixture
def auth_controller(db_session):
    """Provides an AuthController instance."""
    return AuthController(EmployeeRepository(db_session))


def test_management_can_create_employee(auth_controller):
    """Verify Management role has administrative permissions."""
    auth_controller.current_user_data = {"department": "MANAGEMENT"}
    assert auth_controller.check_user_permission("create_employee") is True


def test_sales_cannot_create_employee(auth_controller):
    """Verify Sales role is restricted from administrative tasks."""
    auth_controller.current_user_data = {"department": "SALES"}
    assert auth_controller.check_user_permission("create_employee") is False


def test_sales_can_create_client(auth_controller):
    """Verify Sales role can perform their core business tasks."""
    auth_controller.current_user_data = {"department": "SALES"}
    assert auth_controller.check_user_permission("create_client") is True


def test_support_restrictions(auth_controller):
    """Verify Support role cannot perform Sales or Management tasks."""
    auth_controller.current_user_data = {"department": "SUPPORT"}
    # Can update events
    assert auth_controller.check_user_permission("update_event") is True
    # Cannot create contracts
    assert auth_controller.check_user_permission("create_contract") is False