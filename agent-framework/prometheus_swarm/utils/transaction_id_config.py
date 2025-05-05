from typing import Optional, Union
from dataclasses import dataclass, field
from datetime import timedelta


@dataclass
class TransactionIDTimeWindowConfig:
    """
    Configuration for defining time windows and rules for transaction IDs.

    Attributes:
        max_window_duration (timedelta): Maximum allowed duration for a transaction ID time window.
        min_window_duration (timedelta, optional): Minimum required duration for a transaction ID time window.
        default_window_duration (timedelta): Default duration for a transaction ID time window if not specified.
        max_future_offset (timedelta, optional): Maximum allowed offset into the future for a transaction ID.
        max_past_offset (timedelta, optional): Maximum allowed offset into the past for a transaction ID.
    """

    max_window_duration: timedelta = field(default=timedelta(hours=24))
    min_window_duration: Optional[timedelta] = field(default=timedelta(minutes=1))
    default_window_duration: timedelta = field(default=timedelta(hours=1))
    max_future_offset: Optional[timedelta] = field(default=timedelta(minutes=5))
    max_past_offset: Optional[timedelta] = field(default=timedelta(hours=24))

    def validate_window_duration(self, window_duration: Union[timedelta, int]) -> timedelta:
        """
        Validate the window duration against configuration rules.

        Args:
            window_duration (Union[timedelta, int]): Window duration to validate.

        Returns:
            timedelta: Validated window duration.

        Raises:
            ValueError: If window duration is invalid.
        """
        # Convert int to timedelta if needed
        if isinstance(window_duration, int):
            window_duration = timedelta(seconds=window_duration)

        # Check against max window duration
        if window_duration > self.max_window_duration:
            raise ValueError(f"Window duration exceeds maximum of {self.max_window_duration}")

        # Check against minimum window duration if specified
        if self.min_window_duration and window_duration < self.min_window_duration:
            raise ValueError(f"Window duration is less than minimum of {self.min_window_duration}")

        return window_duration

    def get_window_duration(self, window_duration: Optional[Union[timedelta, int]] = None) -> timedelta:
        """
        Get the appropriate window duration, using default if not specified.

        Args:
            window_duration (Optional[Union[timedelta, int]], optional): Custom window duration.

        Returns:
            timedelta: Validated window duration.
        """
        if window_duration is None:
            return self.default_window_duration
        
        return self.validate_window_duration(window_duration)