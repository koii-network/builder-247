from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from enum import Enum as PyEnum
from datetime import datetime

Base = declarative_base()

class TransactionStatus(PyEnum):
    """Enumeration of possible transaction statuses."""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class Transaction(Base):
    """
    Represents a financial or system transaction in the tracking database.
    
    Attributes:
        id (int): Unique identifier for the transaction
        transaction_type (str): Type of transaction (e.g., 'deposit', 'withdrawal')
        amount (float): Transaction amount
        currency (str): Currency of the transaction
        status (TransactionStatus): Current status of the transaction
        timestamp (datetime): Timestamp when the transaction was initiated
        description (str, optional): Additional description or notes about the transaction
        user_id (int, optional): Foreign key to link transaction to a user
        reference_id (str, optional): External reference or tracking ID
    """
    __tablename__ = 'transactions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    transaction_type = Column(String(50), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String(10), nullable=False)
    status = Column(Enum(TransactionStatus), default=TransactionStatus.PENDING, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    description = Column(String(255), nullable=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    reference_id = Column(String(100), nullable=True, unique=True)
    
    # Optional relationship with user model (assuming it exists)
    user = relationship("User", back_populates="transactions")
    
    def __repr__(self):
        return (f"&lt;Transaction(id={self.id}, type={self.transaction_type}, "
                f"amount={self.amount}, status={self.status})&gt;")

def create_transaction_tables(engine):
    """
    Create all transaction-related database tables.
    
    Args:
        engine: SQLAlchemy database engine
    """
    Base.metadata.create_all(engine)