"""
Utility module for configuring transaction ID time window settings.

This module provides functionality to manage and validate transaction ID time window
configurations, ensuring proper tracking and management of transaction IDs.
"""

from typing import Optional, Union
import time


class TransactionIDConfig:
    """
    Configuration class for managing transaction ID time window settings.

    Attributes:
        _time_window (float): Time window for transaction ID tracking in seconds.
        _max_transactions (Optional[int]): Maximum number of transactions allowed in the time window.
    """

    def __init__(
        self, 
        time_window: float = 60.0, 
        max_transactions: Optional[int] = None
    ):
        """
        Initialize transaction ID configuration.

        Args:
            time_window (float, optional): Duration of time window in seconds. Defaults to 60 seconds.
            max_transactions (Optional[int], optional): Maximum transactions allowed. Defaults to None.

        Raises:
            ValueError: If time_window is not a positive number.
        """
        if time_window <= 0:
            raise ValueError("Time window must be a positive number")

        self._time_window = time_window
        self._max_transactions = max_transactions
        self._transaction_log = []

    def is_transaction_allowed(self) -> bool:
        """
        Check if a new transaction is allowed based on time window and max transactions.

        Returns:
            bool: True if transaction is allowed, False otherwise.
        """
        current_time = time.time()
        
        # Remove transactions outside the time window
        self._transaction_log = [
            timestamp for timestamp in self._transaction_log 
            if current_time - timestamp <= self._time_window
        ]

        # Check max transactions if set
        if self._max_transactions is not None:
            if len(self._transaction_log) >= self._max_transactions:
                return False

        # Record current transaction
        self._transaction_log.append(current_time)
        return True

    def get_time_window(self) -> float:
        """
        Get the current time window duration.

        Returns:
            float: Time window in seconds.
        """
        return self._time_window

    def set_time_window(self, time_window: float) -> None:
        """
        Set a new time window duration.

        Args:
            time_window (float): New time window in seconds.

        Raises:
            ValueError: If time_window is not a positive number.
        """
        if time_window <= 0:
            raise ValueError("Time window must be a positive number")
        
        self._time_window = time_window

    def get_max_transactions(self) -> Optional[int]:
        """
        Get the maximum number of transactions allowed.

        Returns:
            Optional[int]: Maximum transactions or None if not set.
        """
        return self._max_transactions

    def set_max_transactions(self, max_transactions: Optional[int]) -> None:
        """
        Set the maximum number of transactions allowed.

        Args:
            max_transactions (Optional[int]): Maximum transactions to set.

        Raises:
            ValueError: If max_transactions is not a positive integer.
        """
        if max_transactions is not None and max_transactions <= 0:
            raise ValueError("Max transactions must be a positive integer")
        
        self._max_transactions = max_transactions