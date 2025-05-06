from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime

from .nonce_models import Nonce

class NonceStorageInterface:
    """
    Interface for nonce storage and management operations.
    Provides methods for creating, validating, and tracking nonces.
    """

    def create_nonce(self, purpose: Optional[str] = None, validity_minutes: int = 15) -> str:
        """
        Create a new nonce token.
        
        Args:
            purpose (str, optional): Context or purpose of the nonce
            validity_minutes (int, optional): Minutes until nonce expires
        
        Returns:
            str: Generated nonce token
        """
        raise NotImplementedError("Subclass must implement create_nonce method")

    def validate_nonce(self, token: str, purpose: Optional[str] = None) -> bool:
        """
        Validate a nonce token.
        
        Args:
            token (str): Nonce token to validate
            purpose (str, optional): Optional purpose to validate against
        
        Returns:
            bool: True if nonce is valid, False otherwise
        """
        raise NotImplementedError("Subclass must implement validate_nonce method")

    def consume_nonce(self, token: str) -> bool:
        """
        Consume a nonce token, marking it as used.
        
        Args:
            token (str): Nonce token to consume
        
        Returns:
            bool: True if nonce was successfully consumed, False otherwise
        """
        raise NotImplementedError("Subclass must implement consume_nonce method")

class SqlAlchemyNonceStorage(NonceStorageInterface):
    """
    SQLAlchemy implementation of NonceStorageInterface.
    Manages nonce tokens using a SQLAlchemy database session.
    """

    def __init__(self, session: Session):
        """
        Initialize with a SQLAlchemy database session.
        
        Args:
            session (Session): SQLAlchemy database session
        """
        self.session = session

    def create_nonce(self, purpose: Optional[str] = None, validity_minutes: int = 15) -> str:
        """
        Create a new nonce token in the database.
        
        Args:
            purpose (str, optional): Context or purpose of the nonce
            validity_minutes (int, optional): Minutes until nonce expires
        
        Returns:
            str: Generated nonce token
        """
        nonce = Nonce.generate(purpose, validity_minutes)
        self.session.add(nonce)
        self.session.commit()
        return nonce.token

    def validate_nonce(self, token: str, purpose: Optional[str] = None) -> bool:
        """
        Validate a nonce token against database records.
        
        Args:
            token (str): Nonce token to validate
            purpose (str, optional): Optional purpose to validate against
        
        Returns:
            bool: True if nonce is valid, False otherwise
        """
        query = self.session.query(Nonce).filter(
            and_(
                Nonce.token == token,
                Nonce.expires_at > datetime.utcnow(),
                Nonce.used == 0,
                (Nonce.purpose == purpose) if purpose else True
            )
        )
        return query.first() is not None

    def consume_nonce(self, token: str) -> bool:
        """
        Consume a nonce token by marking it as used.
        
        Args:
            token (str): Nonce token to consume
        
        Returns:
            bool: True if nonce was successfully consumed, False otherwise
        """
        nonce = (
            self.session.query(Nonce)
            .filter(
                and_(
                    Nonce.token == token,
                    Nonce.expires_at > datetime.utcnow(),
                    Nonce.used == 0
                )
            )
            .first()
        )
        
        if nonce and nonce.mark_used():
            nonce.used = 1
            self.session.commit()
            return True
        
        return False

    def cleanup_expired_nonces(self) -> int:
        """
        Remove expired nonce tokens from the database.
        
        Returns:
            int: Number of nonces deleted
        """
        expired_nonces = self.session.query(Nonce).filter(
            Nonce.expires_at < datetime.utcnow()
        )
        count = expired_nonces.count()
        expired_nonces.delete(synchronize_session=False)
        self.session.commit()
        return count