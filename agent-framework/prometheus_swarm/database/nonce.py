from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime, timedelta, timezone
import uuid
import hashlib

Base = declarative_base()

class Nonce(Base):
    """
    Represents a nonce (number used once) for security and authentication purposes.
    
    Attributes:
        id (int): Primary key for the nonce record
        value (str): Unique hash generated for the nonce
        created_at (datetime): Timestamp when the nonce was created
        expires_at (datetime): Timestamp when the nonce expires
        context (str): Optional context associated with the nonce
    """
    __tablename__ = 'nonces'

    id = Column(Integer, primary_key=True)
    value = Column(String, unique=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    expires_at = Column(DateTime(timezone=True), nullable=False)
    context = Column(String, nullable=True)

    @classmethod
    def generate(cls, context=None, expiration_minutes=30):
        """
        Generate a new unique nonce.
        
        Args:
            context (str, optional): Additional context for the nonce
            expiration_minutes (int, optional): Minutes until nonce expires. Defaults to 30.
        
        Returns:
            Nonce: A new nonce instance
        """
        # Generate a unique hash using UUID and optional context
        unique_seed = str(uuid.uuid4())
        if context:
            unique_seed += str(context)
        
        nonce_value = hashlib.sha256(unique_seed.encode()).hexdigest()
        now = datetime.now(timezone.utc)
        
        return cls(
            value=nonce_value,
            created_at=now,
            expires_at=now + timedelta(minutes=expiration_minutes),
            context=str(context) if context else None
        )

    def is_valid(self):
        """
        Check if the nonce is still valid (not expired).
        
        Returns:
            bool: True if nonce is valid, False otherwise
        """
        now = datetime.now(timezone.utc)
        
        # Explicitly make the locally stored expires_at timezone-aware if it's not
        expires_at = self.expires_at if self.expires_at.tzinfo else self.expires_at.replace(tzinfo=timezone.utc)
        
        return now < expires_at

    def __repr__(self):
        return f"<Nonce(value={self.value}, expires_at={self.expires_at})>"

class NonceManager:
    """
    Manages nonce operations like creation, validation, and cleanup.
    """
    def __init__(self, session):
        """
        Initialize NonceManager with a database session.
        
        Args:
            session: SQLAlchemy database session
        """
        self.session = session

    def create_nonce(self, context=None, expiration_minutes=30):
        """
        Create and store a new nonce.
        
        Args:
            context (str, optional): Additional context for the nonce
            expiration_minutes (int, optional): Minutes until nonce expires
        
        Returns:
            str: The nonce value
        """
        nonce = Nonce.generate(context, expiration_minutes)
        self.session.add(nonce)
        self.session.commit()
        return nonce.value

    def validate_nonce(self, nonce_value):
        """
        Validate a given nonce value and consume it if valid.
        
        Args:
            nonce_value (str): Nonce to validate
        
        Returns:
            bool: True if nonce is valid and not expired, False otherwise
        """
        nonce = self.session.query(Nonce).filter_by(value=nonce_value).first()
        
        if not nonce:
            return False
        
        if not nonce.is_valid():
            self.session.delete(nonce)
            self.session.commit()
            return False
        
        # Consume the nonce by deleting it
        self.session.delete(nonce)
        self.session.commit()
        return True

    def cleanup_expired_nonces(self):
        """
        Remove all expired nonces from the database.
        
        Returns:
            int: Number of expired nonces removed
        """
        now = datetime.now(timezone.utc)
        expired_nonces = self.session.query(Nonce).filter(
            Nonce.expires_at < now
        ).all()
        
        for nonce in expired_nonces:
            self.session.delete(nonce)
        
        self.session.commit()
        return len(expired_nonces)