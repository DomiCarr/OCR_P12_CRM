# app/models/__init__.py
"""
This module centralizes all SQLAlchemy models to facilitate imports
and ensure they are registered with the Base metadata for migrations.
"""

from app.models.base import Base
from app.models.department import Department
from app.models.employee import Employee
from app.models.client import Client
from app.models.contract import Contract
from app.models.event import Event

__all__ = [
    "Base",
    "Department",
    "Employee",
    "Client",
    "Contract",
    "Event"
]