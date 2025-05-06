"""
Module for handling transaction ID duplication checks.

This module provides functionality to prevent duplicate transaction processing
by tracking and validating transaction IDs.
"""
from typing import Set, Any


class TransactionTracker:
    """
    A thread-safe class to track and validate transaction IDs.

    Attributes:
        _processed_transactions (Set[Any]): A set of processed transaction IDs.
        _max_tracked_transactions (int): Maximum number of transactions to track.
    """

    def __init__(self, max_tracked_transactions: int = 1000):
        """
        Initialize the TransactionTracker.

        Args:
            max_tracked_transactions (int, optional): Maximum number of unique
                transaction IDs to keep track of. Defaults to 1000.
        """
        self._processed_transactions: Set[Any] = set()
        self._transaction_order: list = []
        self._max_tracked_transactions = max_tracked_transactions

    def is_duplicate(self, transaction_id: Any) -> bool:
        """
        Check if a transaction ID is a duplicate.

        Args:
            transaction_id (Any): The transaction ID to check.

        Returns:
            bool: True if the transaction ID is a duplicate, False otherwise.
        """
        if transaction_id in self._processed_transactions:
            return True

        # Add the new transaction
        self._processed_transactions.add(transaction_id)
        self._transaction_order.append(transaction_id)

        # If we've exceeded max tracked transactions, remove the oldest
        if len(self._processed_transactions) > self._max_tracked_transactions:
            oldest_transaction = self._transaction_order.pop(0)
            self._processed_transactions.remove(oldest_transaction)

        return False

    def clear(self) -> None:
        """
        Clear all tracked transaction IDs.
        """
        self._processed_transactions.clear()
        self._transaction_order.clear()