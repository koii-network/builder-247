"""
Module for configuring Transaction ID Time Window Settings.

This module provides functionality to set and manage time window settings
for transaction IDs, allowing customization of how long transaction IDs
are considered valid.
"""

from typing import Union, Optional
import time


class TransactionIDTimeWindowSettings:
    """
    Manages configuration and validation of transaction ID time windows.
    
    Attributes:
        default_time_window (int): Default time window in seconds
        max_time_window (int): Maximum allowed time window in seconds
        min_time_window (int): Minimum allowed time window in seconds
    """
    
    def __init__(
        self, 
        default_time_window: int = 3600,  # 1 hour default
        max_time_window: int = 86400,     # 24 hours max
        min_time_window: int = 60         # 1 minute min
    ):
        """
        Initialize Transaction ID Time Window Settings.
        
        Args:
            default_time_window (int): Default time window in seconds. Defaults to 1 hour.
            max_time_window (int): Maximum allowed time window in seconds. Defaults to 24 hours.
            min_time_window (int): Minimum allowed time window in seconds. Defaults to 1 minute.
        
        Raises:
            ValueError: If input values are invalid or inconsistent.
        """
        if not (min_time_window <= default_time_window <= max_time_window):
            raise ValueError("Time window parameters must be consistent")
        
        self.default_time_window = default_time_window
        self.max_time_window = max_time_window
        self.min_time_window = min_time_window
        self._current_time_window = default_time_window
    
    def set_time_window(self, seconds: int) -> None:
        """
        Set the current time window for transaction IDs.
        
        Args:
            seconds (int): Time window duration in seconds.
        
        Raises:
            ValueError: If the provided time window is outside allowed range.
        """
        if not (self.min_time_window <= seconds <= self.max_time_window):
            raise ValueError(
                f"Time window must be between {self.min_time_window} "
                f"and {self.max_time_window} seconds"
            )
        self._current_time_window = seconds
    
    def get_time_window(self) -> int:
        """
        Get the current time window setting.
        
        Returns:
            int: Current time window in seconds.
        """
        return self._current_time_window
    
    def is_transaction_id_valid(
        self, 
        transaction_id: str, 
        transaction_timestamp: Optional[float] = None
    ) -> bool:
        """
        Check if a transaction ID is valid within the current time window.
        
        Args:
            transaction_id (str): The transaction ID to validate.
            transaction_timestamp (float, optional): Timestamp of the transaction.
                If not provided, uses the current system time.
        
        Returns:
            bool: True if transaction is within time window, False otherwise.
        """
        if not transaction_id:
            return False
        
        if transaction_timestamp is None:
            transaction_timestamp = time.time()
        
        current_time = time.time()
        time_difference = current_time - transaction_timestamp
        
        return time_difference <= self._current_time_window
    
    def reset_to_default(self) -> None:
        """
        Reset time window to the default setting.
        """
        self._current_time_window = self.default_time_window