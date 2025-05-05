from sqlalchemy import Column, Integer, String, DateTime, Boolean, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()

class TransactionID(Base):
    """
    A model to store and manage transaction IDs with comprehensive tracking.
    
    Attributes:
        id (int): Primary key for database
        transaction_uuid (str): Unique identifier for the transaction
        created_at (datetime): Timestamp of transaction creation
        updated_at (datetime): Timestamp of last transaction update
        status (str): Current status of the transaction
        is_completed (bool): Flag indicating transaction completion
        metadata (str): Optional JSON-serializable metadata for additional context
    """
    __tablename__ = 'transaction_ids'

    id = Column(Integer, primary_key=True)
    transaction_uuid = Column(String, default=lambda: str(uuid.uuid4()), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = Column(String(50), default='PENDING')
    is_completed = Column(Boolean, default=False)
    metadata = Column(String, nullable=True)

    __table_args__ = (
        UniqueConstraint('transaction_uuid', name='uq_transaction_uuid'),
    )

    def __repr__(self):
        return f"<TransactionID(uuid='{self.transaction_uuid}', status='{self.status}')>"

    @classmethod
    def create_transaction(cls, status='PENDING', metadata=None):
        """
        Class method to create a new transaction with optional status and metadata.
        
        Args:
            status (str, optional): Initial transaction status. Defaults to 'PENDING'.
            metadata (str, optional): Additional transaction metadata. Defaults to None.
        
        Returns:
            TransactionID: A new transaction instance
        """
        return cls(
            status=status,
            metadata=metadata
        )

    def mark_completed(self):
        """
        Mark the transaction as completed.
        """
        self.is_completed = True
        self.status = 'COMPLETED'

    def update_status(self, new_status):
        """
        Update the transaction status.
        
        Args:
            new_status (str): New status for the transaction
        """
        self.status = new_status