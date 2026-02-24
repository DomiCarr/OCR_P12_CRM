# app/utils/permissions.py
"""
This module provides a centralized authorization system mapping
specific actions to departments to determine user permissions.
"""

import sentry_sdk

# Mapping of permissions per department
PERMISSIONS = {
    'MANAGEMENT': [
        'read_client',
        'update_client',
        'read_contract',
        'create_contract',
        'update_contract',
        'read_event',
        'update_event',
        'read_employee',
        'create_employee',
        'update_employee',
        'delete_employee'
    ],
    'SALES': [
        'read_client',
        'create_client',
        'update_client',
        'read_contract',
        'update_contract',
        'read_event',
        'create_event'
    ],
    'SUPPORT': [
        'read_client',
        'read_contract',
        'read_event',
        'update_event'
    ]
}


def has_permission(action: str, department_name: str) -> bool:
    """
    Check if a specific department has the required permission.
    """
    allowed_actions = PERMISSIONS.get(department_name, [])
    is_allowed = action in allowed_actions

    if not is_allowed:
        # Log unauthorized access attempts to Sentry as a warning
        sentry_sdk.capture_message(
            f"Access denied: Department '{department_name}' "
            f"tried to perform action '{action}'",
            level="warning"
        )

    return is_allowed