from typing import Optional, Dict, Any
from uuid import uuid4
from datetime import datetime, timedelta

class Nonce:
    """
    Represents a unique nonce (number used once) for security and idempotency purposes.

    Attributes:
        id (str): Unique identifier for the nonce
        value (str): The actual nonce value
        created_at (datetime): Timestamp of nonce creation
        expires_at (datetime): Timestamp when nonce expires
        used (bool): Whether the nonce has been used
        metadata (Dict[str, Any]): Optional additional metadata
    """

    def __init__(
        self, 
        value: Optional[str] = None, 
        expires_in: int = 3600,  # Default 1 hour expiration
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a new Nonce instance.

        Args:
            value (Optional[str]): Optional custom nonce value. If None, generates a UUID.
            expires_in (int): Seconds until nonce expires. Defaults to 1 hour.
            metadata (Optional[Dict[str, Any]]): Optional metadata associated with the nonce.
        """
        self.id = str(uuid4())
        self.value = value or str(uuid4())
        self.created_at = datetime.utcnow()
        self.expires_at = self.created_at + timedelta(seconds=expires_in)
        self.used = False
        self.metadata = metadata or {}

    def is_expired(self) -> bool:
        """
        Check if the nonce has expired.

        Returns:
            bool: True if nonce is expired, False otherwise.
        """
        return datetime.utcnow() > self.expires_at

    def mark_as_used(self) -> None:
        """Mark the nonce as used."""
        self.used = True

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert Nonce to a dictionary representation.

        Returns:
            Dict[str, Any]: Dictionary representation of the nonce.
        """
        return {
            'id': self.id,
            'value': self.value,
            'created_at': self.created_at.isoformat(),
            'expires_at': self.expires_at.isoformat(),
            'used': self.used,
            'metadata': self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Nonce':
        """
        Create a Nonce instance from a dictionary.

        Args:
            data (Dict[str, Any]): Dictionary representation of a nonce.

        Returns:
            Nonce: Reconstructed Nonce instance.
        """
        nonce = cls(value=data['value'], metadata=data.get('metadata'))
        nonce.id = data['id']
        nonce.created_at = datetime.fromisoformat(data['created_at'])
        nonce.expires_at = datetime.fromisoformat(data['expires_at'])
        nonce.used = data['used']
        return nonce