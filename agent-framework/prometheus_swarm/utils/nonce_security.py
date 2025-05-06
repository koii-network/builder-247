"""
Nonce Security Configuration Module

This module provides functionality for configuring and managing nonce security parameters.
A nonce (number used once) is a unique, randomly generated value used to prevent replay attacks
and ensure the uniqueness of cryptographic operations.
"""

import secrets
import hashlib
import time
from typing import Dict, Any, Optional


class NonceSecurityConfig:
    """
    A class for managing nonce security configuration and generation.
    """

    def __init__(
        self,
        nonce_length: int = 32,
        nonce_expiration: int = 3600,  # 1 hour default expiration
        allow_reuse: bool = False,
        max_nonce_history: int = 1000
    ):
        """
        Initialize nonce security configuration.

        Args:
            nonce_length (int): Length of generated nonce in bytes. Defaults to 32.
            nonce_expiration (int): Time in seconds before a nonce expires. Defaults to 3600 (1 hour).
            allow_reuse (bool): Whether nonces can be reused. Defaults to False.
            max_nonce_history (int): Maximum number of nonces to track. Defaults to 1000.
        """
        self.nonce_length = nonce_length
        self.nonce_expiration = nonce_expiration
        self.allow_reuse = allow_reuse
        self.max_nonce_history = max_nonce_history
        self._used_nonces: Dict[str, float] = {}

    def generate_nonce(self) -> str:
        """
        Generate a secure random nonce.

        Returns:
            str: A hex-encoded secure random nonce.
        """
        # Use secrets for cryptographically secure random generation
        raw_nonce = secrets.token_bytes(self.nonce_length)
        return raw_nonce.hex()

    def validate_nonce(self, nonce: str) -> bool:
        """
        Validate a nonce based on configured parameters.

        Args:
            nonce (str): The nonce to validate.

        Returns:
            bool: Whether the nonce is valid.
        """
        current_time = time.time()

        # First, clean up expired nonces
        self._cleanup_expired_nonces(current_time)

        # If nonce reuse is allowed, always return True
        if self.allow_reuse:
            return True

        # Check if nonce has been used before
        if nonce in self._used_nonces:
            return False

        # Store the nonce with current timestamp
        self._used_nonces[nonce] = current_time

        # Trim nonce history if it exceeds max size
        if len(self._used_nonces) > self.max_nonce_history:
            oldest_nonce = min(self._used_nonces, key=self._used_nonces.get)
            del self._used_nonces[oldest_nonce]

        return True

    def _cleanup_expired_nonces(self, current_time: float) -> None:
        """
        Remove nonces that have expired from the history.

        Args:
            current_time (float): Current timestamp.
        """
        expired_nonces = [
            nonce for nonce, timestamp in self._used_nonces.items()
            if current_time - timestamp > self.nonce_expiration
        ]
        for nonce in expired_nonces:
            del self._used_nonces[nonce]

    def get_configuration(self) -> Dict[str, Any]:
        """
        Retrieve the current nonce security configuration.

        Returns:
            Dict[str, Any]: A dictionary of configuration parameters.
        """
        return {
            "nonce_length": self.nonce_length,
            "nonce_expiration": self.nonce_expiration,
            "allow_reuse": self.allow_reuse,
            "max_nonce_history": self.max_nonce_history
        }