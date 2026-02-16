# app/models/base.py
"""
This module serves as the foundation for the ORM layer.
- Provides a centralized DeclarativeBase for model registration.
- Defines custom type aliases (Annotated) to standardize SQL constraints
  (String lengths, Primary Keys, and Timestamps) across the entire schema.
- Uses server-side functions for automated audit trails (created_at, updated_at).
"""
import datetime
from typing import Annotated
from sqlalchemy import String, Text, func
from sqlalchemy.orm import DeclarativeBase, mapped_column


# Type aliases to ensure consistency across all models
# Primary keys with auto-increment
pk_id = Annotated[int, mapped_column(primary_key=True, autoincrement=True)]

# Standard string lengths for database columns
str_20 = Annotated[str, mapped_column(String(20))]
str_50 = Annotated[str, mapped_column(String(50))]
str_100 = Annotated[str, mapped_column(String(100))]
str_255 = Annotated[str, mapped_column(String(255))]

# Long text for descriptions or notes
text_type = Annotated[str, mapped_column(Text)]

# Automatically managed timestamps
timestamp_now = Annotated[
    datetime.datetime,
    mapped_column(server_default=func.now())
]
timestamp_update = Annotated[
    datetime.datetime,
    mapped_column(server_default=func.now(), onupdate=func.now())
]


class Base(DeclarativeBase):
    """
    Base class for declarative models.
    Maintains a registry of all mapped classes.
    """
    pass