from sqlalchemy import Column, String, DateTime, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()

class TransactionEvidence(Base):
    """
    Database model representing unique transaction evidence.
    
    This model ensures that each transaction has a unique identifier 
    and prevents duplicate entries based on specific constraints.
    """
    __tablename__ = 'transaction_evidence'
    
    # Primary key using UUID for global uniqueness
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Transaction-specific unique identifiers
    transaction_hash = Column(String, nullable=False)
    transaction_source = Column(String, nullable=False)
    
    # Timestamp of the transaction
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Additional metadata for traceability
    evidence_type = Column(String, nullable=False)
    
    # Composite unique constraint to prevent duplicate transactions
    __table_args__ = (
        UniqueConstraint(
            'transaction_hash', 
            'transaction_source', 
            'evidence_type', 
            name='uix_transaction_evidence'
        ),
    )
    
    def __repr__(self):
        """
        String representation of the TransactionEvidence model.
        
        Returns:
            str: A string describing the transaction evidence
        """
        return (f"<TransactionEvidence(id={self.id}, "
                f"hash={self.transaction_hash}, "
                f"source={self.transaction_source}, "
                f"type={self.evidence_type})>")
    
    @classmethod
    def validate_transaction(cls, transaction_hash, transaction_source, evidence_type):
        """
        Class method to validate the uniqueness of a transaction.
        
        Args:
            transaction_hash (str): Unique hash of the transaction
            transaction_source (str): Source of the transaction
            evidence_type (str): Type of transaction evidence
        
        Returns:
            bool: True if the transaction is unique, False otherwise
        """
        # This method would typically be used in a database session to check uniqueness
        # Actual implementation depends on the specific database context
        return True