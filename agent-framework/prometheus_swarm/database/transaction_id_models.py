from sqlalchemy.orm import declarative_base, DeclarativeBase
from sqlalchemy import Column, Integer, String, DateTime, JSON
from datetime import datetime
from typing import Dict, Any

class Base(DeclarativeBase):
    """Base class for SQLAlchemy models"""
    pass

class TransactionID(Base):
    """
    Model to store and manage transaction IDs across the system.
    
    Attributes:
        id (int): Primary key for the transaction record
        transaction_id (str): Unique identifier for a transaction
        source (str): Origin of the transaction (e.g., 'github', 'local', 'external')
        transaction_metadata (dict): Additional context or details about the transaction
        created_at (datetime): Timestamp when the transaction was recorded
        updated_at (datetime): Timestamp of the last update to the transaction
    """
    __tablename__ = 'transaction_ids'

    id = Column(Integer, primary_key=True, autoincrement=True)
    transaction_id = Column(String, unique=True, nullable=False, index=True)
    source = Column(String, nullable=False)
    transaction_metadata = Column('metadata', JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        """
        String representation of the TransactionID instance.
        
        Returns:
            str: A concise description of the transaction
        """
        return f"<TransactionID(id='{self.transaction_id}', source='{self.source}')>"