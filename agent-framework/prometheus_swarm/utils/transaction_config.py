"""
Transaction ID Time Window Configuration Module

This module provides functionality to configure and manage 
transaction ID time window settings.
"""

from typing import Optional, Union
from datetime import datetime, timedelta


class TransactionTimeWindowConfig:
    """
    Configuration class for managing transaction ID time windows.
    
    Attributes:
        window_size (timedelta): The size of the time window
        max_transactions (Optional[int]): Maximum number of transactions allowed in the window
    """

    def __init__(
        self, 
        window_size: Optional[Union[int, timedelta]] = None, 
        max_transactions: Optional[int] = None
    ):
        """
        Initialize the transaction time window configuration.
        
        Args:
            window_size (Optional[Union[int, timedelta]]): Size of the time window in seconds or as a timedelta.
                If int, represents seconds. If None, defaults to 1 hour.
            max_transactions (Optional[int]): Maximum number of transactions allowed in the window.
                If None, no limit is applied.
        
        Raises:
            ValueError: If window_size is invalid or negative.
        """
        # Convert window_size to timedelta if it's an integer
        if isinstance(window_size, int):
            if window_size < 0:
                raise ValueError("Window size cannot be negative")
            self.window_size = timedelta(seconds=window_size)
        elif isinstance(window_size, timedelta):
            if window_size.total_seconds() < 0:
                raise ValueError("Window size cannot be negative")
            self.window_size = window_size
        elif window_size is None:
            # Default to 1 hour if not specified
            self.window_size = timedelta(hours=1)
        else:
            raise TypeError("window_size must be int, timedelta, or None")

        # Validate max_transactions
        if max_transactions is not None and max_transactions < 0:
            raise ValueError("Maximum transactions cannot be negative")
        
        self.max_transactions = max_transactions

    def is_within_window(
        self, 
        transaction_timestamp: datetime, 
        current_time: Optional[datetime] = None
    ) -> bool:
        """
        Check if a transaction timestamp is within the configured time window.
        
        Args:
            transaction_timestamp (datetime): Timestamp of the transaction
            current_time (Optional[datetime]): Reference time to check against. 
                If None, uses the current system time.
        
        Returns:
            bool: True if the transaction is within the time window, False otherwise
        """
        if current_time is None:
            current_time = datetime.now()

        # Check if transaction is within the time window
        return (current_time - transaction_timestamp) <= self.window_size

    def validate_transaction_count(
        self, 
        transaction_timestamps: list[datetime], 
        current_time: Optional[datetime] = None
    ) -> bool:
        """
        Validate if the number of transactions within the time window is within the limit.
        
        Args:
            transaction_timestamps (list[datetime]): List of transaction timestamps
            current_time (Optional[datetime]): Reference time to check against. 
                If None, uses the current system time.
        
        Returns:
            bool: True if the number of transactions is within the limit, False otherwise
        """
        if current_time is None:
            current_time = datetime.now()

        # Filter transactions within the time window
        transactions_in_window = [
            ts for ts in transaction_timestamps 
            if self.is_within_window(ts, current_time)
        ]

        # If max_transactions is not set, always return True
        if self.max_transactions is None:
            return True

        # Check if number of transactions exceeds the limit
        return len(transactions_in_window) < self.max_transactions