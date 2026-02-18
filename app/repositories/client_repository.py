# app/repositories/client_repository.py
"""
Data access layer for Client-specific operations.
"""

from sqlalchemy.orm import Session
from app.models.client import Client
from app.repositories.base_repository import BaseRepository


class ClientRepository(BaseRepository[Client]):
    """
    Repository handling Client database queries.
    """

    def __init__(self, session: Session):
        super().__init__(session, Client)

    def get_all_clients(self):
        """
        Fetch all clients by calling the inherited get_all method.
        """
        return self.get_all()

    def get_by_email(self, email: str):
        """
        Fetch a client by its unique email.
        """
        return self.session.query(self.model).filter(
            self.model.email == email
        ).first()