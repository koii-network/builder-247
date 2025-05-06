"""
Utility module for checking transaction ID duplication.

This module provides functionality to check and prevent duplicate transaction IDs.
"""
from typing import List, Dict, Any


class TransactionIDDuplicateChecker:
    """
    A class to manage and check for duplicate transaction IDs.
    """

    def __init__(self, max_stored_ids: int = 1000):
        """
        Initialize the duplicate checker.

        :param max_stored_ids: Maximum number of transaction IDs to keep track of
        """
        self._transaction_ids: List[str] = []
        self._max_stored_ids = max_stored_ids

    def is_duplicate(self, transaction_id: str) -> bool:
        """
        Check if a transaction ID is a duplicate.

        :param transaction_id: The transaction ID to check
        :return: True if the transaction ID is a duplicate, False otherwise
        """
        if not transaction_id:
            raise ValueError("Transaction ID cannot be empty or None")

        if transaction_id in self._transaction_ids:
            return True

        # Add the new transaction ID
        self._transaction_ids.append(transaction_id)

        # Maintain max stored IDs
        if len(self._transaction_ids) > self._max_stored_ids:
            self._transaction_ids.pop(0)

        return False

    def clear(self) -> None:
        """
        Clear all stored transaction IDs.
        """
        self._transaction_ids.clear()

    def get_stored_ids(self) -> List[str]:
        """
        Get the current list of stored transaction IDs.

        :return: List of stored transaction IDs
        """
        return self._transaction_ids.copy()