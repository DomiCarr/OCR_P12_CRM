# app/utils/permissions.py
"""
This module provides a centralized authorization system using an
Access Control Matrix (ACM). It maps specific actions to departments
to determine user permissions across the application.
"""

from enum import Enum


class DepartmentName(Enum):
    """Enumeration of existing departments."""

    MANAGEMENT = "MANAGEMENT"
    SALES = "SALES"
    SUPPORT = "SUPPORT"


# The Permission Matrix: (Action, Department)
# Use a set for O(1) lookups and clear mapping.
PERMISSION_MATRIX = {
    ("manage_employees", DepartmentName.MANAGEMENT.value),
    ("manage_contracts", DepartmentName.MANAGEMENT.value),
    ("manage_contracts", DepartmentName.SALES.value),
    ("update_events", DepartmentName.MANAGEMENT.value),
    ("update_events", DepartmentName.SUPPORT.value),
}


def has_permission(action: str, department_name: str) -> bool:
    """
    Check if a specific couple (action, department) exists in the matrix.
    """
    return (action, department_name) in PERMISSION_MATRIX