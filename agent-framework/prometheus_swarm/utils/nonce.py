import threading
import time
from typing import Dict, Optional


class NonceTracker:
    """
    A thread-safe nonce tracking mechanism to prevent replay attacks and 
    manage unique request identifiers.
    """

    def __init__(self, max_age_seconds: int = 3600):
        """
        Initialize the NonceTracker.

        Args:
            max_age_seconds (int, optional): Maximum time a nonce is considered valid.
                Defaults to 1 hour (3600 seconds).
        """
        self._nonce_store: Dict[str, float] = {}
        self._lock = threading.Lock()
        self._max_age = max_age_seconds

    def generate_nonce(self, prefix: str = "") -> str:
        """
        Generate a unique nonce.

        Args:
            prefix (str, optional): Optional prefix for the nonce. Defaults to "".

        Returns:
            str: A unique nonce string.
        """
        current_time = time.time()
        nonce = f"{prefix}{current_time}"

        with self._lock:
            self._nonce_store[nonce] = current_time
            self._cleanup_expired_nonces()

        return nonce

    def validate_nonce(self, nonce: str) -> bool:
        """
        Validate a given nonce.

        Args:
            nonce (str): The nonce to validate.

        Returns:
            bool: True if the nonce is valid and not previously used, False otherwise.
        """
        current_time = time.time()

        with self._lock:
            # Check if nonce exists
            if nonce not in self._nonce_store:
                return False

            # Check nonce age
            nonce_time = self._nonce_store[nonce]
            if current_time - nonce_time > self._max_age:
                del self._nonce_store[nonce]
                return False

            # Mark nonce as used by removing it
            del self._nonce_store[nonce]
            return True

    def _cleanup_expired_nonces(self) -> None:
        """
        Remove expired nonces from the store.
        This method should be called with the lock held.
        """
        current_time = time.time()
        expired_nonces = [
            nonce for nonce, timestamp in self._nonce_store.items()
            if current_time - timestamp > self._max_age
        ]

        for nonce in expired_nonces:
            del self._nonce_store[nonce]