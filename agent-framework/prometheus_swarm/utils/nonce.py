"""
Nonce Configuration Management Module

This module provides utilities for generating, managing, and validating nonces
to prevent replay attacks and ensure request uniqueness.
"""

import hashlib
import time
import uuid
from typing import Dict, Optional


class NonceManager:
    """
    Manages nonce generation, tracking, and validation.

    Attributes:
        _used_nonces (Dict[str, float]): Tracks used nonces and their timestamps
        _nonce_expiry_seconds (int): Expiration time for nonces
    """

    def __init__(self, nonce_expiry_seconds: int = 300):
        """
        Initialize NonceManager.

        Args:
            nonce_expiry_seconds (int, optional): Nonce expiration time. Defaults to 300 seconds.
        """
        self._used_nonces: Dict[str, float] = {}
        self._nonce_expiry_seconds = nonce_expiry_seconds

    def generate_nonce(self) -> str:
        """
        Generate a unique, secure nonce.

        Returns:
            str: A unique nonce string
        """
        unique_input = f"{uuid.uuid4()}{time.time()}"
        return hashlib.sha256(unique_input.encode()).hexdigest()

    def validate_nonce(self, nonce: str) -> bool:
        """
        Validate a nonce, checking for uniqueness and expiration.

        Args:
            nonce (str): Nonce to validate

        Returns:
            bool: Whether the nonce is valid and can be used
        """
        current_time = time.time()

        # Remove expired nonces
        self._cleanup_expired_nonces(current_time)

        # Check if nonce has been used
        if nonce in self._used_nonces:
            return False

        # Mark nonce as used
        self._used_nonces[nonce] = current_time
        return True

    def _cleanup_expired_nonces(self, current_time: float) -> None:
        """
        Remove nonces that have exceeded the expiration time.

        Args:
            current_time (float): Current timestamp
        """
        expired_nonces = [
            n for n, timestamp in self._used_nonces.items()
            if current_time - timestamp > self._nonce_expiry_seconds
        ]
        for nonce in expired_nonces:
            del self._used_nonces[nonce]