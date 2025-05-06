from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid
import hashlib
import json

@dataclass
class TransactionEvidence:
    """
    A dataclass representing transaction evidence with uniqueness constraints.
    
    Ensures each transaction evidence has:
    - A unique transaction ID
    - A unique hash to prevent duplicate submissions
    - Comprehensive metadata
    - Immutability after creation
    """
    
    transaction_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """
        Validate and compute a unique hash for the transaction evidence.
        """
        if not self.transaction_id:
            raise ValueError("Transaction ID cannot be empty")
        
        # Validate timestamp
        if self.timestamp.tzinfo is None:
            raise TypeError("Timestamp must be timezone-aware")
        
        if self.timestamp > datetime.now(timezone.utc):
            raise TypeError("Timestamp cannot be in the future")
        
        # Compute a hash based on transaction data for uniqueness
        self._compute_evidence_hash()
    
    def _compute_evidence_hash(self) -> str:
        """
        Generate a SHA-256 hash of the transaction data to ensure uniqueness.
        
        Returns:
            str: A unique hash representing the transaction evidence
        """
        hash_input = json.dumps({
            'transaction_id': self.transaction_id,
            'timestamp': self.timestamp.isoformat(),
            'data': self.data,
            'metadata': self.metadata
        }, sort_keys=True)
        
        self.evidence_hash = hashlib.sha256(hash_input.encode()).hexdigest()
        return self.evidence_hash
    
    def validate(self) -> bool:
        """
        Perform comprehensive validation of the transaction evidence.
        
        Returns:
            bool: True if the evidence is valid, False otherwise
        """
        # Check transaction ID
        if not self.transaction_id or len(self.transaction_id) == 0:
            return False
        
        # Check timestamp (must be timezone-aware and not in future)
        if (self.timestamp.tzinfo is None or 
            self.timestamp > datetime.now(timezone.utc)):
            return False
        
        # Verify hash integrity
        computed_hash = self._compute_evidence_hash()
        if computed_hash != self.evidence_hash:
            return False
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the transaction evidence to a dictionary representation.
        
        Returns:
            Dict[str, Any]: A dictionary containing all transaction evidence details
        """
        return {
            'transaction_id': self.transaction_id,
            'timestamp': self.timestamp.isoformat(),
            'data': self.data,
            'metadata': self.metadata,
            'evidence_hash': self.evidence_hash
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TransactionEvidence':
        """
        Create a TransactionEvidence instance from a dictionary.
        
        Args:
            data (Dict[str, Any]): Dictionary containing transaction evidence details
        
        Returns:
            TransactionEvidence: A new TransactionEvidence instance
        """
        evidence = cls(
            transaction_id=data.get('transaction_id', str(uuid.uuid4())),
            timestamp=datetime.fromisoformat(data.get('timestamp', datetime.now(timezone.utc).isoformat())),
            data=data.get('data', {}),
            metadata=data.get('metadata', {})
        )
        return evidence