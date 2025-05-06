from sqlalchemy import Column, Integer, String, Float, DateTime, Enum
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func
from enum import Enum as PyEnum
from typing import Optional
from datetime import datetime

Base = declarative_base()

class TransactionType(PyEnum):
    """Enumeration of transaction types."""
    DEPOSIT = 'deposit'
    WITHDRAWAL = 'withdrawal'
    TRANSFER = 'transfer'
    PURCHASE = 'purchase'
    REFUND = 'refund'

class Transaction(Base):
    """
    SQLAlchemy model representing a financial transaction.

    Attributes:
        id (int): Unique identifier for the transaction.
        amount (float): Transaction amount in the base currency.
        transaction_type (TransactionType): Type of transaction.
        description (Optional[str]): Optional description of the transaction.
        timestamp (datetime): Timestamp of when the transaction occurred.
        source_account (Optional[str]): Source account identifier.
        destination_account (Optional[str]): Destination account identifier.
        status (str): Transaction processing status.
    """
    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    amount = Column(Float, nullable=False)
    transaction_type = Column(Enum(TransactionType), nullable=False)
    description = Column(String(255), nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    source_account = Column(String(100), nullable=True)
    destination_account = Column(String(100), nullable=True)
    status = Column(String(50), nullable=False, default='completed', server_default='completed')

    def __init__(self, *args, **kwargs):
        """
        Initialize a Transaction object.

        If no status is provided, defaults to 'completed'.
        """
        if 'status' not in kwargs:
            kwargs['status'] = 'completed'
        super().__init__(*args, **kwargs)

    def __repr__(self) -> str:
        """
        Returns a string representation of the transaction.

        Returns:
            str: A formatted string describing the transaction.
        """
        return (f"&lt;Transaction(id={self.id}, "
                f"amount={self.amount}, "
                f"type={self.transaction_type.value}, "
                f"timestamp={self.timestamp})&gt;")

    def validate(self) -> bool:
        """
        Validates the transaction attributes.

        Returns:
            bool: True if the transaction is valid, False otherwise.
        """
        if self.amount <= 0:
            return False
        
        if self.transaction_type in [TransactionType.TRANSFER, 
                                      TransactionType.WITHDRAWAL] and not self.source_account:
            return False
        
        if self.transaction_type in [TransactionType.TRANSFER, 
                                      TransactionType.DEPOSIT] and not self.destination_account:
            return False
        
        return True