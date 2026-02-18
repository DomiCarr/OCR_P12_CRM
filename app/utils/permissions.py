# app/utils/permissions.py
"""
This module provides a centralized authorization system mapping
specific actions to departments to determine user permissions.
"""

# Mapping of permissions per department
PERMISSIONS = {
    'MANAGEMENT': [
        'read_client',
        'read_contract',
        'read_event',
        'update_contract',
        'update_event',
        'manage_employees'
    ],
    'SALES': [
        'read_client',
        'read_contract',
        'read_event',
        'create_client',
        'update_client',
        'create_contract',
        'update_contract',
        'manage_contracts'
    ],
    'SUPPORT': [
        'read_client',
        'read_contract',
        'read_event',
        'update_events'
    ]
}


def has_permission(action: str, department_name: str) -> bool:
    """
    Check if a specific department has the required permission.
    """
    allowed_actions = PERMISSIONS.get(department_name, [])
    return action in allowed_actions