# app/repositories/contract_repository.py
"""
Data access layer for Contract-specific operations.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.contract import Contract
from app.repositories.base_repository import BaseRepository


class ContractRepository(BaseRepository[Contract]):
    """
    Repository handling Contract database queries.
    """

    def __init__(self, session: Session):
        super().__init__(session, Contract)

    def get_all_contracts(self) -> List[Contract]:
        """
        Fetch all contracts by calling the inherited get_all method.
        """
        return self.get_all()

    def get_unsigned_contracts(self) -> List[Contract]:
        """
        Fetch all contracts that are not yet signed.
        """
        return self.session.query(self.model).filter(
            self.model.is_signed == False  # noqa: E712
        ).all()

    def get_unpaid_contracts(self) -> List[Contract]:
        """
        Fetch contracts where remaining amount is greater than zero.
        """
        return self.session.query(self.model).filter(
            self.model.remaining_amount > 0
        ).all()