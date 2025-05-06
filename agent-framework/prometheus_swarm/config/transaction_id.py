"""
Configuration module for Transaction ID Time Window Settings.

This module provides functionality to configure and manage 
transaction ID time window settings.
"""

from typing import Optional, Union
from datetime import timedelta

class TransactionIDConfig:
    """
    Configuration class for managing Transaction ID time window settings.
    
    Attributes:
        _default_time_window (timedelta): Default time window for transaction IDs
        _custom_time_window (Optional[timedelta]): Custom time window if set
    """
    
    def __init__(self, default_window_minutes: int = 60):
        """
        Initialize TransactionIDConfig with default or custom time window.
        
        Args:
            default_window_minutes (int, optional): Time window in minutes. Defaults to 60.
        """
        self._default_time_window = timedelta(minutes=default_window_minutes)
        self._custom_time_window: Optional[timedelta] = None
    
    def set_time_window(self, window_minutes: Union[int, float]) -> None:
        """
        Set a custom time window for transaction IDs.
        
        Args:
            window_minutes (Union[int, float]): Time window in minutes.
        
        Raises:
            ValueError: If window_minutes is less than or equal to 0.
        """
        if window_minutes <= 0:
            raise ValueError("Time window must be a positive number")
        
        self._custom_time_window = timedelta(minutes=window_minutes)
    
    def get_time_window(self) -> timedelta:
        """
        Retrieve the current time window.
        
        Returns:
            timedelta: Current time window, either custom or default.
        """
        return self._custom_time_window or self._default_time_window
    
    def reset_time_window(self) -> None:
        """
        Reset the time window to the default setting.
        """
        self._custom_time_window = None