# app/repositories/contract_repository.py
"""
Data access layer for Contract-specific operations.
"""

from sqlalchemy.orm import Session
from app.models.contract import Contract
from app.repositories.base_repository import BaseRepository


class ContractRepository(BaseRepository[Contract]):
    """
    Repository handling Contract database queries.
    """

    def __init__(self, session: Session):
        super().__init__(session, Contract)
