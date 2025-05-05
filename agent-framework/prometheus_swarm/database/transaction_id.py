from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class TransactionID(Base):
    """
    Database model for storing and tracking transaction IDs.
    
    Attributes:
        id (int): Primary key for the transaction record
        transaction_id (str): Unique identifier for the transaction
        context (str): Context or type of transaction
        timestamp (DateTime): Timestamp of transaction creation
        status (str): Current status of the transaction
        metadata (str, optional): Additional metadata about the transaction
    """
    __tablename__ = 'transaction_ids'

    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(String, unique=True, index=True, nullable=False)
    context = Column(String, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String, default='pending')
    metadata = Column(String, nullable=True)

    @classmethod
    def create(cls, transaction_id, context, status='pending', metadata=None):
        """
        Class method to create a new transaction ID record.
        
        Args:
            transaction_id (str): Unique transaction identifier
            context (str): Transaction context
            status (str, optional): Transaction status. Defaults to 'pending'
            metadata (str, optional): Additional transaction metadata
        
        Returns:
            TransactionID: New transaction record
        """
        return cls(
            transaction_id=transaction_id,
            context=context,
            status=status,
            metadata=metadata
        )

    def update_status(self, new_status):
        """
        Update the status of the transaction.
        
        Args:
            new_status (str): New status to set for the transaction
        """
        self.status = new_status

    def __repr__(self):
        """
        String representation of the TransactionID.
        
        Returns:
            str: Formatted string with transaction details
        """
        return f"<TransactionID(id={self.id}, transaction_id='{self.transaction_id}', context='{self.context}', status='{self.status}')>"