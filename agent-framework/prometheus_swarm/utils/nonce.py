"""
Nonce (Number Used Once) Tracking Mechanism

This module provides a thread-safe mechanism for tracking and managing nonces
to prevent replay attacks and ensure unique request processing.

Key Features:
- Thread-safe nonce generation and validation
- Configurable nonce expiration
- Support for multiple nonce spaces
"""

import threading
from typing import Dict, Any
from time import time


class NonceTracker:
    """
    A thread-safe class for tracking and validating nonces.

    Attributes:
        _nonce_store (Dict[str, Dict[str, Any]]): Stores nonces with their metadata
        _lock (threading.Lock): Thread synchronization lock
        _max_age (float): Maximum age of a valid nonce in seconds
    """

    def __init__(self, max_age: float = 3600):
        """
        Initialize a NonceTracker.

        Args:
            max_age (float, optional): Maximum age of a valid nonce in seconds. 
                Defaults to 1 hour (3600 seconds).
        """
        self._nonce_store: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()
        self._max_age = max_age

    def generate_nonce(self, namespace: str = 'default') -> str:
        """
        Generate a unique nonce for a given namespace.

        Args:
            namespace (str, optional): Namespace for nonce tracking. Defaults to 'default'.

        Returns:
            str: A unique nonce value
        """
        import uuid
        import hashlib

        with self._lock:
            # Create a time-based and UUID-based nonce
            raw_nonce = f"{time()}:{uuid.uuid4()}"
            nonce = hashlib.sha256(raw_nonce.encode()).hexdigest()

            # Store nonce metadata
            if namespace not in self._nonce_store:
                self._nonce_store[namespace] = {}

            self._nonce_store[namespace][nonce] = {
                'timestamp': time(),
                'used': False
            }

            return nonce

    def validate_nonce(self, nonce: str, namespace: str = 'default', use_once: bool = True) -> bool:
        """
        Validate a nonce in a given namespace.

        Args:
            nonce (str): Nonce to validate
            namespace (str, optional): Namespace for nonce tracking. Defaults to 'default'.
            use_once (bool, optional): Whether nonce can be used only once. Defaults to True.

        Returns:
            bool: True if nonce is valid, False otherwise
        """
        with self._lock:
            # Clean expired nonces
            self._cleanup_nonces(namespace)

            # Check if namespace exists
            if namespace not in self._nonce_store:
                return False

            # Check if nonce exists
            if nonce not in self._nonce_store[namespace]:
                return False

            nonce_data = self._nonce_store[namespace][nonce]

            # Check if nonce is already used (if use_once is True)
            if use_once and nonce_data['used']:
                return False

            # Mark nonce as used if use_once is True
            if use_once:
                nonce_data['used'] = True

            return True

    def _cleanup_nonces(self, namespace: str):
        """
        Remove expired nonces from the store.

        Args:
            namespace (str): Namespace to clean
        """
        current_time = time()
        if namespace in self._nonce_store:
            self._nonce_store[namespace] = {
                k: v for k, v in self._nonce_store[namespace].items()
                if current_time - v['timestamp'] <= self._max_age
            }