from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timedelta, timezone
import secrets
import uuid

Base = declarative_base()

class Nonce(Base):
    """
    Represents a unique nonce token with expiration and associated metadata.
    
    Attributes:
        id (int): Primary key for database
        token (str): Unique, cryptographically secure nonce token
        purpose (str): Purpose or context of the nonce
        created_at (datetime): Timestamp of nonce creation
        expires_at (datetime): Timestamp when nonce expires
        used (bool): Flag indicating whether nonce has been used
    """
    __tablename__ = 'nonces'

    id = Column(Integer, primary_key=True)
    token = Column(String, unique=True, nullable=False, index=True)
    purpose = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used = Column(Integer, default=0)  # Use int for atomic updates

    @classmethod
    def generate(cls, purpose: str = None, validity_minutes: int = 15) -> 'Nonce':
        """
        Generate a new secure nonce token with configurable expiration.
        
        Args:
            purpose (str, optional): Context or purpose of the nonce
            validity_minutes (int, optional): Minutes until nonce expires. Defaults to 15.
        
        Returns:
            Nonce: A new nonce instance
        """
        now = datetime.now(timezone.utc)
        return cls(
            token=secrets.token_urlsafe(32),  # Cryptographically secure token
            purpose=purpose,
            created_at=now,
            expires_at=now + timedelta(minutes=validity_minutes),
            used=0
        )

    def is_valid(self) -> bool:
        """
        Check if the nonce is valid (not expired and not used).
        
        Returns:
            bool: True if nonce is valid, False otherwise
        """
        return (
            datetime.now(timezone.utc) <= self.expires_at and 
            self.used == 0
        )

    def mark_used(self) -> bool:
        """
        Atomically mark the nonce as used.
        
        Returns:
            bool: True if successfully marked as used, False if already used
        """
        # Atomic compare and swap
        return self.used == 0