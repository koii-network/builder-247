from sqlalchemy import Column, String, DateTime, JSON, Boolean, Integer, UniqueConstraint
from sqlalchemy.orm import declarative_base
from datetime import datetime
import uuid
import hashlib
import json

Base = declarative_base()

class TransactionEvidence(Base):
    """
    Schema for tracking unique transaction evidence with comprehensive validation.
    
    Ensures uniqueness through:
    - Unique transaction ID
    - Unique hash of transaction contents
    - Immutable core attributes
    """
    
    __tablename__ = 'transaction_evidence'
    
    # Primary identifiers
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    transaction_hash = Column(String(64), unique=True, nullable=False)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Transaction details
    source = Column(String(255), nullable=False)
    destination = Column(String(255), nullable=False)
    amount = Column(Integer, nullable=False)
    currency = Column(String(10), nullable=False)
    
    # Status tracking
    is_verified = Column(Boolean, default=False)
    verification_attempts = Column(Integer, default=0)
    
    # Arbitrary transaction metadata
    extra_data = Column(JSON, nullable=True)
    
    # Uniqueness constraint
    __table_args__ = (
        UniqueConstraint('transaction_hash', name='uq_transaction_hash'),
    )
    
    @classmethod
    def generate_transaction_hash(cls, transaction_data):
        """
        Generate a deterministic hash for transaction data.
        
        Args:
            transaction_data (dict): Transaction details to hash
        
        Returns:
            str: SHA-256 hash of the sorted transaction data
        """
        # Sort to ensure consistent hash generation
        sorted_data = json.dumps(transaction_data, sort_keys=True)
        return hashlib.sha256(sorted_data.encode()).hexdigest()
    
    def validate(self):
        """
        Validate transaction evidence integrity.
        
        Returns:
            bool: Whether the transaction is valid
        """
        # Basic validation checks
        validations = [
            self.amount > 0,
            len(self.source) > 0,
            len(self.destination) > 0,
            len(self.currency) > 0
        ]
        
        return all(validations)
    
    def __repr__(self):
        return (f"<TransactionEvidence(id={self.id}, "
                f"source={self.source}, "
                f"destination={self.destination}, "
                f"amount={self.amount})>")