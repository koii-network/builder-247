"""
Module for configuring Transaction ID Time Window Settings.

This module provides configuration and management of transaction ID time windows,
allowing flexible control over transaction tracking and expiration.
"""
from typing import Optional
import time


class TransactionIDSettings:
    """
    Manages configuration and validation of Transaction ID time windows.

    Attributes:
        time_window (int): Duration in seconds for which a transaction ID remains valid.
        max_stored_transactions (Optional[int]): Maximum number of transactions to store.
    """

    def __init__(
        self,
        time_window: int = 3600,  # Default 1 hour
        max_stored_transactions: Optional[int] = 1000
    ):
        """
        Initialize Transaction ID Time Window Settings.

        Args:
            time_window (int, optional): Time in seconds a transaction remains valid. Defaults to 3600 (1 hour).
            max_stored_transactions (Optional[int], optional): Maximum transactions to track. Defaults to 1000.
        
        Raises:
            ValueError: If time_window is negative or max_stored_transactions is non-positive.
        """
        if time_window < 0:
            raise ValueError("Time window must be non-negative")
        
        if max_stored_transactions is not None and max_stored_transactions <= 0:
            raise ValueError("Maximum stored transactions must be positive")

        self.time_window = time_window
        self.max_stored_transactions = max_stored_transactions
        self._transactions = {}

    def add_transaction(self, transaction_id: str) -> bool:
        """
        Add a new transaction ID to tracking.

        Args:
            transaction_id (str): Unique identifier for the transaction.

        Returns:
            bool: True if transaction was successfully added, False if already exists or window is full.
        """
        current_time = time.time()

        # Clean up expired transactions
        self._clean_expired_transactions(current_time)

        # Check if transaction already exists
        if transaction_id in self._transactions:
            return False

        # Check if max transactions limit is reached
        if (self.max_stored_transactions is not None and
            len(self._transactions) >= self.max_stored_transactions):
            return False

        self._transactions[transaction_id] = current_time
        return True

    def is_transaction_valid(self, transaction_id: str) -> bool:
        """
        Check if a transaction ID is valid within the current time window.

        Args:
            transaction_id (str): Transaction ID to validate.

        Returns:
            bool: True if transaction is valid, False otherwise.
        """
        current_time = time.time()
        self._clean_expired_transactions(current_time)

        if transaction_id not in self._transactions:
            return False

        transaction_time = self._transactions[transaction_id]
        return current_time - transaction_time <= self.time_window

    def _clean_expired_transactions(self, current_time: float) -> None:
        """
        Remove transactions that have expired from the tracking dictionary.

        Args:
            current_time (float): Current timestamp for comparison.
        """
        self._transactions = {
            tid: timestamp for tid, timestamp in self._transactions.items()
            if current_time - timestamp <= self.time_window
        }