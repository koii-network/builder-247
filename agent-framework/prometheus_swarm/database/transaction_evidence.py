from sqlalchemy import Column, String, DateTime, JSON, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()

class TransactionEvidence(Base):
    """
    SQLAlchemy model representing transaction evidence with uniqueness constraints.
    Ensures that each transaction evidence entry is unique based on specific attributes.
    """
    __tablename__ = 'transaction_evidence'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    transaction_hash = Column(String(100), nullable=False)
    transaction_type = Column(String(50), nullable=False)
    evidence_data = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Unique constraint to prevent duplicate transaction evidence
    __table_args__ = (
        UniqueConstraint('transaction_hash', 'transaction_type', name='_transaction_evidence_uc'),
    )

    def __repr__(self):
        """
        String representation of the TransactionEvidence model.
        """
        return f"<TransactionEvidence(id={self.id}, transaction_hash={self.transaction_hash}, transaction_type={self.transaction_type})>"

def validate_transaction_evidence(transaction_hash, transaction_type, evidence_data):
    """
    Validate transaction evidence before creating a new entry.

    Args:
        transaction_hash (str): Unique hash of the transaction
        transaction_type (str): Type of the transaction
        evidence_data (dict): JSON-serializable data representing the transaction evidence

    Raises:
        ValueError: If the input data is invalid
    """
    if not transaction_hash:
        raise ValueError("Transaction hash is required")
    
    if not transaction_type:
        raise ValueError("Transaction type is required")
    
    if not isinstance(evidence_data, dict):
        raise ValueError("Evidence data must be a dictionary")

    # Optional: Add more specific validation rules
    return True