import uuid
import time
from typing import Dict, Optional, Any

class NonceRequestInterface:
    """
    A class to manage nonce (number used once) generation and validation.

    Attributes:
        _nonce_store (Dict[str, Dict[str, Any]]): A store to track generated nonces.
        _nonce_expiry_seconds (int): Duration for which a nonce remains valid.
    """

    def __init__(self, nonce_expiry_seconds: int = 300):
        """
        Initialize the NonceRequestInterface.

        Args:
            nonce_expiry_seconds (int, optional): Time in seconds after which a nonce expires.
                Defaults to 300 seconds (5 minutes).
        """
        self._nonce_store: Dict[str, Dict[str, Any]] = {}
        self._nonce_expiry_seconds = nonce_expiry_seconds

    def generate_nonce(self, context: Optional[str] = None) -> str:
        """
        Generate a unique nonce for a given context.

        Args:
            context (str, optional): An optional context or identifier for the nonce.
                Allows for more specific nonce tracking.

        Returns:
            str: A unique nonce value.
        """
        nonce = str(uuid.uuid4())
        current_time = time.time()

        nonce_entry = {
            'created_at': current_time,
            'context': context,
            'used': False
        }

        self._nonce_store[nonce] = nonce_entry
        self._cleanup_expired_nonces()

        return nonce

    def validate_nonce(self, nonce: str, context: Optional[str] = None) -> bool:
        """
        Validate a nonce, checking its existence, expiry, and usage status.

        Args:
            nonce (str): The nonce to validate.
            context (str, optional): Optional context to match against the nonce.

        Returns:
            bool: True if the nonce is valid, False otherwise.
        """
        self._cleanup_expired_nonces()

        # Check if nonce exists
        if nonce not in self._nonce_store:
            return False

        nonce_entry = self._nonce_store[nonce]

        # Check context if provided
        if context is not None and nonce_entry['context'] != context:
            return False

        # Check if nonce has already been used
        if nonce_entry['used']:
            return False

        # Check nonce expiry
        current_time = time.time()
        if current_time - nonce_entry['created_at'] > self._nonce_expiry_seconds:
            return False

        # Mark nonce as used
        nonce_entry['used'] = True
        return True

    def _cleanup_expired_nonces(self):
        """
        Remove expired and used nonces from the nonce store.
        """
        current_time = time.time()
        expired_nonces = [
            nonce for nonce, entry in self._nonce_store.items()
            if entry['used'] or 
               current_time - entry['created_at'] > self._nonce_expiry_seconds
        ]

        for nonce in expired_nonces:
            del self._nonce_store[nonce]