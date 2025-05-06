"""Nonce Management and Error Handling Module.

This module provides utilities for managing nonces, preventing replay attacks,
and handling nonce-related errors with structured logging.
"""

import time
from typing import Dict, Any, Optional
from .logging import logger, log_error
from .errors import ClientAPIError


class NonceError(ClientAPIError):
    """Custom exception for nonce-related errors."""

    def __init__(self, message: str, error_type: str = "nonce_error"):
        """
        Initialize a NonceError with a specific message and error type.

        Args:
            message (str): Detailed error message
            error_type (str, optional): Type of nonce error. Defaults to "nonce_error".
        """
        super().__init__(Exception(message))
        self.error_type = error_type


class NonceManager:
    """
    Manages nonce generation, validation, and tracking.

    Prevents replay attacks by ensuring unique nonces and managing their lifecycle.
    """

    def __init__(self, max_age: int = 3600, max_uses: int = 1):
        """
        Initialize the NonceManager.

        Args:
            max_age (int, optional): Maximum age of a nonce in seconds. Defaults to 1 hour.
            max_uses (int, optional): Maximum number of times a nonce can be used. Defaults to 1.
        """
        self._nonces: Dict[str, Dict[str, Any]] = {}
        self._max_age = max_age
        self._max_uses = max_uses

    def generate_nonce(self, context: Optional[str] = None) -> str:
        """
        Generate a unique nonce for a given context.

        Args:
            context (str, optional): Additional context for the nonce. Defaults to None.

        Returns:
            str: A unique nonce value
        """
        import uuid
        
        # Generate a UUID and include timestamp
        nonce = f"{uuid.uuid4()}:{int(time.time())}"
        
        # Store nonce details
        self._nonces[nonce] = {
            "created_at": time.time(),
            "context": context,
            "uses": 0
        }
        
        logger.info(f"Generated nonce: {nonce} (Context: {context or 'None'})")
        return nonce

    def validate_nonce(self, nonce: str, context: Optional[str] = None) -> bool:
        """
        Validate a nonce, checking its age, usage, and optional context.

        Args:
            nonce (str): Nonce to validate
            context (str, optional): Expected context for the nonce. Defaults to None.

        Raises:
            NonceError: If nonce is invalid, expired, or overused

        Returns:
            bool: True if nonce is valid
        """
        current_time = time.time()
        
        # Check if nonce exists
        if nonce not in self._nonces:
            log_error(NonceError("Nonce not found", "nonce_not_found"))
            raise NonceError("Invalid nonce: Not found", "nonce_not_found")
        
        nonce_data = self._nonces[nonce]
        
        # Check nonce age
        if current_time - nonce_data['created_at'] > self._max_age:
            del self._nonces[nonce]
            log_error(NonceError("Nonce expired", "nonce_expired"))
            raise NonceError("Invalid nonce: Expired", "nonce_expired")
        
        # Check context if provided
        if context is not None and nonce_data.get('context') != context:
            log_error(NonceError("Context mismatch", "nonce_context_mismatch"))
            raise NonceError("Invalid nonce: Context mismatch", "nonce_context_mismatch")
        
        # Check usage count
        nonce_data['uses'] += 1
        if nonce_data['uses'] > self._max_uses:
            del self._nonces[nonce]
            log_error(NonceError("Nonce overused", "nonce_overused"))
            raise NonceError("Invalid nonce: Overused", "nonce_overused")
        
        logger.info(f"Validated nonce: {nonce}")
        return True

    def remove_nonce(self, nonce: str) -> None:
        """
        Manually remove a nonce from tracking.

        Args:
            nonce (str): Nonce to remove
        """
        if nonce in self._nonces:
            del self._nonces[nonce]
            logger.info(f"Nonce manually removed: {nonce}")

    def cleanup_expired_nonces(self) -> int:
        """
        Remove expired nonces from tracking.

        Returns:
            int: Number of nonces removed
        """
        current_time = time.time()
        expired_nonces = [
            nonce for nonce, data in self._nonces.items()
            if current_time - data['created_at'] > self._max_age
        ]
        
        for nonce in expired_nonces:
            del self._nonces[nonce]
        
        if expired_nonces:
            logger.info(f"Cleaned up {len(expired_nonces)} expired nonces")
        
        return len(expired_nonces)