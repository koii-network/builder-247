"""
Module for managing transaction expiration and cleanup.

This module provides functionality to track and clean up expired transactions
from the database based on configurable expiration parameters.
"""

from datetime import datetime, timedelta
from typing import List, Optional, Type, TypeVar
import datetime as dt

from sqlalchemy import Column, DateTime, func
from sqlalchemy.orm import Session

ModelType = TypeVar('ModelType')

class TransactionExpirationMixin:
    """
    A mixin class to add expiration tracking to database models.

    Attributes:
        created_at (DateTime): Timestamp of when the record was created
        expires_at (DateTime): Timestamp of when the record will expire
    """
    created_at = Column(DateTime, default=func.now())
    expires_at = Column(DateTime, nullable=True)

    @classmethod
    def cleanup_expired_transactions(
        cls: Type[ModelType], 
        db_session: Session, 
        expiration_hours: int = 24
    ) -> List[ModelType]:
        """
        Remove transactions that have expired.

        Args:
            db_session (Session): Database session
            expiration_hours (int, optional): Hours after which a transaction expires. 
                Defaults to 24 hours.

        Returns:
            List[ModelType]: List of expired transactions that were deleted
        """
        now = dt.datetime.now(dt.timezone.utc)
        expiration_time = now - dt.timedelta(hours=expiration_hours)

        # Find expired transactions
        expired_transactions = (
            db_session.query(cls)
            .filter(
                # Transactions with explicit expiration that have passed
                ((cls.expires_at < now) & (cls.expires_at != None)) | 
                # Transactions without explicit expiration that are too old
                ((cls.expires_at == None) & (cls.created_at < expiration_time))
            )
            .all()
        )

        # Delete expired transactions
        for transaction in expired_transactions:
            db_session.delete(transaction)

        db_session.commit()
        return expired_transactions

    def set_expiration(self, hours: int = 24) -> None:
        """
        Set expiration time for a transaction.

        Args:
            hours (int, optional): Number of hours until expiration. 
                Defaults to 24 hours.
        """
        self.expires_at = dt.datetime.now(dt.timezone.utc) + dt.timedelta(hours=hours)