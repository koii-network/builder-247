from abc import ABC, abstractmethod
from typing import Optional, List
from .nonce import Nonce

class NonceStorageInterface(ABC):
    """
    Abstract base class defining the interface for Nonce storage operations.
    Provides a standardized way to interact with nonce storage, allowing 
    for different backend implementations.
    """

    @abstractmethod
    def store_nonce(self, nonce: Nonce) -> None:
        """
        Store a new nonce in the storage system.

        Args:
            nonce (Nonce): The nonce to be stored.

        Raises:
            ValueError: If a nonce with the same value already exists.
        """
        pass

    @abstractmethod
    def get_nonce(self, nonce_value: str) -> Optional[Nonce]:
        """
        Retrieve a nonce by its value.

        Args:
            nonce_value (str): The unique value of the nonce.

        Returns:
            Optional[Nonce]: The nonce if found, None otherwise.
        """
        pass

    @abstractmethod
    def validate_nonce(self, nonce_value: str) -> bool:
        """
        Validate a nonce, checking for existence, expiration, and usage.

        Args:
            nonce_value (str): The nonce value to validate.

        Returns:
            bool: True if nonce is valid and unused, False otherwise.
        """
        pass

    @abstractmethod
    def mark_nonce_as_used(self, nonce_value: str) -> None:
        """
        Mark a specific nonce as used.

        Args:
            nonce_value (str): The nonce value to mark.

        Raises:
            ValueError: If the nonce does not exist.
        """
        pass

    @abstractmethod
    def cleanup_expired_nonces(self) -> int:
        """
        Remove all expired nonces from storage.

        Returns:
            int: Number of expired nonces removed.
        """
        pass


class InMemoryNonceStorage(NonceStorageInterface):
    """
    In-memory implementation of NonceStorageInterface for testing and development.
    """

    def __init__(self):
        """Initialize an empty nonce storage."""
        self._nonces = {}

    def store_nonce(self, nonce: Nonce) -> None:
        """
        Store a new nonce in memory.

        Args:
            nonce (Nonce): The nonce to be stored.

        Raises:
            ValueError: If a nonce with the same value already exists.
        """
        if nonce.value in self._nonces:
            raise ValueError(f"Nonce with value {nonce.value} already exists")
        self._nonces[nonce.value] = nonce

    def get_nonce(self, nonce_value: str) -> Optional[Nonce]:
        """
        Retrieve a nonce by its value from memory.

        Args:
            nonce_value (str): The unique value of the nonce.

        Returns:
            Optional[Nonce]: The nonce if found, None otherwise.
        """
        return self._nonces.get(nonce_value)

    def validate_nonce(self, nonce_value: str) -> bool:
        """
        Validate a nonce, checking for existence, expiration, and usage.

        Args:
            nonce_value (str): The nonce value to validate.

        Returns:
            bool: True if nonce is valid and unused, False otherwise.
        """
        nonce = self.get_nonce(nonce_value)
        return (
            nonce is not None 
            and not nonce.is_expired() 
            and not nonce.used
        )

    def mark_nonce_as_used(self, nonce_value: str) -> None:
        """
        Mark a specific nonce as used.

        Args:
            nonce_value (str): The nonce value to mark.

        Raises:
            ValueError: If the nonce does not exist.
        """
        nonce = self.get_nonce(nonce_value)
        if nonce is None:
            raise ValueError(f"Nonce with value {nonce_value} not found")
        nonce.mark_as_used()

    def cleanup_expired_nonces(self) -> int:
        """
        Remove all expired nonces from memory.

        Returns:
            int: Number of expired nonces removed.
        """
        initial_count = len(self._nonces)
        self._nonces = {
            value: nonce for value, nonce in self._nonces.items()
            if not nonce.is_expired()
        }
        return initial_count - len(self._nonces)