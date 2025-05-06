from sqlalchemy import Column, String, DateTime, UUID, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base
import uuid

class TransactionEvidence(Base):
    """
    Database model for Transaction Evidence with uniqueness constraints.
    
    Ensures each transaction evidence record is unique based on multiple attributes.
    """
    __tablename__ = 'transaction_evidence'
    
    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Transaction-specific fields
    transaction_hash = Column(String, nullable=False)
    transaction_type = Column(String, nullable=False)
    
    # Timestamp fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Optional foreign key reference (adjust as needed)
    # user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    
    # Uniqueness Constraints
    __table_args__ = (
        # Ensure unique combination of transaction hash and type
        UniqueConstraint('transaction_hash', 'transaction_type', name='uq_transaction_evidence'),
    )
    
    def __repr__(self):
        """
        String representation of the TransactionEvidence model.
        
        Returns:
            str: A string describing the transaction evidence
        """
        return f"<TransactionEvidence(id={self.id}, hash={self.transaction_hash}, type={self.transaction_type})>"
    
    @classmethod
    def validate_transaction_evidence(cls, transaction_hash, transaction_type):
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
        
        # Add any additional validation logic here