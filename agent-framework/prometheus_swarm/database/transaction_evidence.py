"""Transaction Evidence Model."""

from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field, UniqueConstraint
import uuid

class TransactionEvidence(SQLModel, table=True):
    """
    Database model for Transaction Evidence with uniqueness constraints.
    
    Ensures each transaction evidence record is unique based on multiple attributes.
    """
    # Custom table name in the database
    __tablename__ = 'transaction_evidence'
    
    # Primary Key
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    
    # Transaction-specific fields
    transaction_hash: str = Field(index=True, unique=True)
    transaction_type: str
    
    # Timestamp fields
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    
    # Optional additional fields can be added here
    
    @classmethod
    def validate_transaction_evidence(cls, transaction_hash: str, transaction_type: str):
        """
        Validate transaction evidence before creation.
        
        Args:
            transaction_hash (str): Unique hash of the transaction
            transaction_type (str): Type of the transaction
        
        Raises:
            ValueError: If transaction evidence is invalid
        """
        if not transaction_hash or not isinstance(transaction_hash, str):
            raise ValueError("Transaction hash must be a non-empty string")
        
        if not transaction_type or not isinstance(transaction_type, str):
            raise ValueError("Transaction type must be a non-empty string")
        
        # Optional: Add more specific validation rules here