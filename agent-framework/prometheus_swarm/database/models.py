from sqlalchemy import Column, Integer, String, DateTime, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()

class TransactionID(Base):
    """
    Model for storing unique transaction identifiers with additional metadata.
    
    Attributes:
        id (int): Primary key for database indexing
        transaction_uuid (str): Unique universal identifier for the transaction
        source (str): Origin or context of the transaction
        created_at (datetime): Timestamp of transaction ID creation
        metadata (str, optional): Additional JSON-serializable metadata about the transaction
    """
    __tablename__ = 'transaction_ids'
    
    id = Column(Integer, primary_key=True)
    transaction_uuid = Column(String, unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    source = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    metadata = Column(String, nullable=True)
    
    # Ensure uniqueness of transaction_uuid
    __table_args__ = (
        UniqueConstraint('transaction_uuid', name='uq_transaction_uuid'),
    )
    
    def __repr__(self):
        """
        String representation of the TransactionID instance.
        
        Returns:
            str: A descriptive string of the transaction ID
        """
        return f"<TransactionID(uuid='{self.transaction_uuid}', source='{self.source}', created_at='{self.created_at}')>"
    
    @classmethod
    def create(cls, source: str, metadata: str = None):
        """
        Class method to create a new TransactionID instance.
        
        Args:
            source (str): Origin or context of the transaction
            metadata (str, optional): Additional metadata about the transaction
        
        Returns:
            TransactionID: A new transaction ID instance
        """
        return cls(
            source=source,
            metadata=metadata
        )