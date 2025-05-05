"""
Transaction ID Time Window Configuration Module.

This module defines the configuration and validation for transaction ID time windows.
"""

from typing import Optional, Union
from datetime import timedelta


class TransactionIDTimeWindowConfig:
    """
    Configuration class for Transaction ID Time Window settings.

    Attributes:
        max_window_duration (timedelta): Maximum allowed time window for transaction IDs.
        min_window_duration (timedelta): Minimum allowed time window for transaction IDs.
        default_window_duration (timedelta): Default time window duration.
    """

    def __init__(
        self,
        max_window_duration: Optional[Union[int, timedelta]] = timedelta(hours=24),
        min_window_duration: Optional[Union[int, timedelta]] = timedelta(minutes=5),
        default_window_duration: Optional[Union[int, timedelta]] = timedelta(hours=1)
    ):
        """
        Initialize Transaction ID Time Window Configuration.

        Args:
            max_window_duration (Optional[Union[int, timedelta]]): Maximum time window duration.
                Defaults to 24 hours.
            min_window_duration (Optional[Union[int, timedelta]]): Minimum time window duration.
                Defaults to 5 minutes.
            default_window_duration (Optional[Union[int, timedelta]]): Default time window duration.
                Defaults to 1 hour.

        Raises:
            ValueError: If time window configurations are invalid.
        """
        # Convert integer seconds to timedelta if needed
        max_window_duration = (
            timedelta(seconds=max_window_duration)
            if isinstance(max_window_duration, int)
            else max_window_duration
        )
        min_window_duration = (
            timedelta(seconds=min_window_duration)
            if isinstance(min_window_duration, int)
            else min_window_duration
        )
        default_window_duration = (
            timedelta(seconds=default_window_duration)
            if isinstance(default_window_duration, int)
            else default_window_duration
        )

        # Validate time window configurations
        if min_window_duration > max_window_duration:
            raise ValueError("Minimum window duration cannot exceed maximum window duration")

        if default_window_duration < min_window_duration:
            raise ValueError("Default window duration cannot be less than minimum window duration")

        if default_window_duration > max_window_duration:
            raise ValueError("Default window duration cannot exceed maximum window duration")

        self.max_window_duration = max_window_duration
        self.min_window_duration = min_window_duration
        self.default_window_duration = default_window_duration

    def validate_window_duration(self, window_duration: Union[int, timedelta]) -> timedelta:
        """
        Validate and normalize a transaction ID time window duration.

        Args:
            window_duration (Union[int, timedelta]): Time window duration to validate.

        Returns:
            timedelta: Validated and normalized time window duration.

        Raises:
            ValueError: If window duration is invalid.
        """
        # Convert integer seconds to timedelta if needed
        window_duration = (
            timedelta(seconds=window_duration)
            if isinstance(window_duration, int)
            else window_duration
        )

        if window_duration < self.min_window_duration:
            raise ValueError(f"Window duration must be at least {self.min_window_duration}")

        if window_duration > self.max_window_duration:
            raise ValueError(f"Window duration cannot exceed {self.max_window_duration}")

        return window_duration

    def get_default_window_duration(self) -> timedelta:
        """
        Get the default transaction ID time window duration.

        Returns:
            timedelta: Default time window duration.
        """
        return self.default_window_duration