# tests/test_permissions.py
"""
Unit tests for the authorization system.

Tests included:
- test_management_permissions: Validate all actions for MANAGEMENT.
- test_sales_permissions: Validate allowed and restricted actions for SALES.
- test_support_permissions: Validate allowed and restricted actions for SUPPORT.
- test_unknown_department_permissions: Ensure unknown departments have no access.
"""

from app.utils.permissions import has_permission


def test_management_permissions():
    """Verify that MANAGEMENT has all its assigned permissions."""
    dept = "MANAGEMENT"
    assert has_permission("create_employee", dept) is True
    assert has_permission("delete_employee", dept) is True
    assert has_permission("update_contract", dept) is True


def test_sales_permissions():
    """Verify SALES permissions and restrictions."""
    dept = "SALES"
    # Allowed
    assert has_permission("create_client", dept) is True
    assert has_permission("create_event", dept) is True
    # Restricted
    assert has_permission("create_employee", dept) is False
    assert has_permission("delete_employee", dept) is False


def test_support_permissions():
    """Verify SUPPORT permissions and restrictions."""
    dept = "SUPPORT"
    # Allowed
    assert has_permission("read_event", dept) is True
    assert has_permission("update_event", dept) is True
    # Restricted
    assert has_permission("create_client", dept) is False
    assert has_permission("create_contract", dept) is False


def test_unknown_department_permissions():
    """Ensure that a non-existent department has no permissions."""
    assert has_permission("read_client", "GHOST_DEPT") is False