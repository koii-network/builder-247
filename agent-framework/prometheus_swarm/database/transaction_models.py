from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from enum import Enum as PyEnum
from datetime import datetime

Base = declarative_base()

class TransactionStatus(PyEnum):
    """Enum representing possible transaction statuses."""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class Transaction(Base):
    """
    Database model representing a financial transaction.
    
    Attributes:
        id (int): Unique identifier for the transaction
        transaction_id (str): External transaction identifier
        source_account (str): Source account for the transaction
        destination_account (str): Destination account for the transaction
        amount (float): Transaction amount
        currency (str): Currency of the transaction
        status (TransactionStatus): Current status of the transaction
        timestamp (datetime): Timestamp of the transaction
        description (str, optional): Additional transaction description
        category (str, optional): Transaction category
    """
    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    transaction_id = Column(String, unique=True, nullable=False, index=True)
    source_account = Column(String, nullable=False)
    destination_account = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String(3), nullable=False)
    status = Column(Enum(TransactionStatus), nullable=False, default=TransactionStatus.PENDING)
    timestamp = Column(DateTime, default=datetime.utcnow)
    description = Column(String, nullable=True)
    category = Column(String, nullable=True)

    def __repr__(self):
        """String representation of the Transaction."""
        return (f"&lt;Transaction(id={self.id}, "
                f"transaction_id='{self.transaction_id}', "
                f"amount={self.amount} {self.currency}, "
                f"status={self.status})&gt;")