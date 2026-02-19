# app/repositories/base_repository.py
"""
This module defines the BaseRepository class using Generics.
It provides a standardized interface for common database operations (CRUD)
shared across all specific repositories.
"""

from typing import Generic, TypeVar, Type, Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
import sentry_sdk
from app.models.base import Base

T = TypeVar("T", bound=Base)


class BaseRepository(Generic[T]):
    """
    Base class for data access logic.
    """

    def __init__(self, session: Session, model: Type[T]):
        self.session = session
        self.model = model

    def get_by_id(self, obj_id: int) -> Optional[T]:
        """Fetch a single record by its primary key."""
        return self.session.query(self.model).filter(
            self.model.id == obj_id
        ).first()

    def get_all(self) -> List[T]:
        """Fetch all records for this model."""
        return self.session.query(self.model).all()

    def add(self, obj: T) -> T:
        """Add a new object and commit the transaction."""
        try:
            self.session.add(obj)
            self.session.commit()
            self.session.refresh(obj)
            return obj
        except IntegrityError as e:
            # Capture database constraint violations (e.g., duplicate email)
            self.session.rollback()
            sentry_sdk.capture_exception(e)
            raise e
        except SQLAlchemyError as e:
            # Capture any other database-related errors
            self.session.rollback()
            sentry_sdk.capture_exception(e)
            raise e

    def update(self, obj_id: int, update_data: dict) -> Optional[T]:
        """Update a record and commit the transaction."""
        obj = self.get_by_id(obj_id)
        if obj:
            try:
                for key, value in update_data.items():
                    if hasattr(obj, key):
                        setattr(obj, key, value)
                self.session.commit()
                self.session.refresh(obj)
                return obj
            except SQLAlchemyError as e:
                self.session.rollback()
                sentry_sdk.capture_exception(e)
                raise e
        return None

    def delete(self, obj: T) -> None:
        """Remove an object and commit the transaction."""
        try:
            self.session.delete(obj)
            self.session.commit()
        except SQLAlchemyError as e:
            self.session.rollback()
            sentry_sdk.capture_exception(e)
            raise e