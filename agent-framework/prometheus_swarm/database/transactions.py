from sqlalchemy import Column, Integer, String, Float, DateTime, Enum
from sqlalchemy.ext.declarative import declarative_base
from enum import Enum as PyEnum
from datetime import datetime

Base = declarative_base()

class TransactionStatus(PyEnum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELED = "canceled"

class Transaction(Base):
    """
    Represents a financial or system transaction with comprehensive tracking
    """
    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    transaction_type = Column(String(50), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String(10), nullable=False)
    
    # Track transaction lifecycle
    status = Column(Enum(TransactionStatus), default=TransactionStatus.PENDING)
    
    # Timestamps for lifecycle tracking
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Optional reference fields
    reference_id = Column(String(100), nullable=True)
    description = Column(String(255), nullable=True)
    
    # Sender and recipient information
    sender_id = Column(String(100), nullable=False)
    recipient_id = Column(String(100), nullable=False)

    def __repr__(self):
        return f"&lt;Transaction(id={self.id}, type={self.transaction_type}, amount={self.amount}, status={self.status})&gt;"

def initialize_transaction_table(engine):
    """
    Create the transactions table in the database
    
    :param engine: SQLAlchemy database engine
    """
    Base.metadata.create_all(engine)