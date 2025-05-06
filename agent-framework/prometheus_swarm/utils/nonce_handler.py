"""Nonce Error Handling and Logging Module.

This module provides robust nonce handling with advanced error logging 
and custom exception mechanisms for tracking and mitigating nonce-related issues.
"""

import time
import hashlib
import threading
from typing import Dict, Optional, Union, Any
from .logging import logger, log_error

class NonceError(Exception):
    """Custom exception for nonce-related errors."""
    def __init__(self, message: str, error_type: str = 'NONCE_ERROR'):
        """
        Initialize a NonceError with a specific message and type.

        Args:
            message (str): Detailed error description
            error_type (str, optional): Type of nonce error. Defaults to 'NONCE_ERROR'.
        """
        self.error_type = error_type
        super().__init__(f"{error_type}: {message}")


class NonceManager:
    """
    Thread-safe nonce management system with advanced error handling and logging.

    Manages nonce generation, tracking, and validation with configurable 
    security parameters.
    """

    def __init__(
        self, 
        nonce_ttl: int = 300,  # 5 minutes default
        max_nonce_attempts: int = 3,
        require_unique: bool = True
    ):
        """
        Initialize NonceManager with configurable security parameters.

        Args:
            nonce_ttl (int): Time-to-live for nonces in seconds
            max_nonce_attempts (int): Maximum attempts to generate a unique nonce
            require_unique (bool): Whether to require globally unique nonces
        """
        self._nonce_ttl = nonce_ttl
        self._max_nonce_attempts = max_nonce_attempts
        self._require_unique = require_unique
        self._nonce_store: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()

    def generate_nonce(
        self, 
        context: Optional[str] = None, 
        secret_key: Optional[str] = None
    ) -> str:
        """
        Generate a cryptographically secure nonce with optional context.

        Args:
            context (str, optional): Additional context for nonce generation
            secret_key (str, optional): Secret key to enhance nonce entropy

        Returns:
            str: A unique, time-bound nonce
        
        Raises:
            NonceError: If unable to generate a unique nonce
        """
        with self._lock:
            current_time = time.time()
            base_string = f"{current_time}{context or ''}{secret_key or ''}"

            for attempt in range(self._max_nonce_attempts):
                # Create a hash to ensure randomness
                nonce = hashlib.sha256(
                    f"{base_string}:{attempt}".encode()
                ).hexdigest()[:16]

                # Check uniqueness if required
                if not self._require_unique or nonce not in self._nonce_store:
                    # Store nonce with metadata
                    self._nonce_store[nonce] = {
                        'created_at': current_time,
                        'context': context,
                        'used': False
                    }
                    return nonce

            # If unique nonce cannot be generated
            log_error(
                NonceError("Failed to generate unique nonce"), 
                context="NONCE_GENERATION"
            )
            raise NonceError(
                "Cannot generate unique nonce after multiple attempts", 
                'NONCE_GENERATION_FAILURE'
            )

    def validate_nonce(
        self, 
        nonce: str, 
        context: Optional[str] = None
    ) -> bool:
        """
        Validate a given nonce.

        Args:
            nonce (str): Nonce to validate
            context (str, optional): Context to further validate nonce

        Returns:
            bool: Whether the nonce is valid

        Raises:
            NonceError: For various nonce validation failures
        """
        with self._lock:
            current_time = time.time()

            # Check if nonce exists
            if nonce not in self._nonce_store:
                log_error(
                    NonceError("Unknown nonce"), 
                    context="NONCE_VALIDATION"
                )
                raise NonceError("Invalid or expired nonce", 'UNKNOWN_NONCE')

            nonce_data = self._nonce_store[nonce]

            # Check time-to-live
            if current_time - nonce_data['created_at'] > self._nonce_ttl:
                del self._nonce_store[nonce]
                log_error(
                    NonceError("Nonce expired"), 
                    context="NONCE_VALIDATION"
                )
                raise NonceError("Nonce has expired", 'NONCE_EXPIRED')

            # Optional context validation
            if context and nonce_data['context'] != context:
                log_error(
                    NonceError("Context mismatch"), 
                    context="NONCE_VALIDATION"
                )
                raise NonceError("Nonce context invalid", 'NONCE_CONTEXT_MISMATCH')

            # Check if nonce has already been used
            if nonce_data['used']:
                log_error(
                    NonceError("Nonce already used"), 
                    context="NONCE_VALIDATION"
                )
                raise NonceError("Nonce has already been consumed", 'NONCE_ALREADY_USED')

            # Mark nonce as used
            nonce_data['used'] = True
            return True

    def cleanup_expired_nonces(self) -> int:
        """
        Clean up expired nonces.

        Returns:
            int: Number of nonces removed
        """
        with self._lock:
            current_time = time.time()
            expired_nonces = [
                nonce for nonce, data in self._nonce_store.items()
                if current_time - data['created_at'] > self._nonce_ttl
            ]

            for nonce in expired_nonces:
                del self._nonce_store[nonce]

            return len(expired_nonces)