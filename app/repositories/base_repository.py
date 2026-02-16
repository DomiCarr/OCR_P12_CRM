# app/repositories/base_repository.py
from typing import Generic, TypeVar, Type, Optional, List
from sqlalchemy.orm import Session
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

    def add(self, obj: T) -> None:
        """Add a new object to the session."""
        self.session.add(obj)

    def delete(self, obj: T) -> None:
        """Remove an object from the session."""
        self.session.delete(obj)