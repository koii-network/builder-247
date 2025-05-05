from typing import Optional, Union
from datetime import timedelta


class TransactionIDTimeWindowConfig:
    """
    Configuration class for managing transaction ID time windows.

    This class allows configuring and validating time windows for transaction IDs,
    supporting absolute and relative time configurations.
    """

    def __init__(
        self,
        max_time_window: Optional[Union[timedelta, int]] = None,
        min_time_window: Optional[Union[timedelta, int]] = None,
        default_time_window: Optional[Union[timedelta, int]] = None
    ):
        """
        Initialize the transaction ID time window configuration.

        Args:
            max_time_window (Optional[Union[timedelta, int]]): Maximum allowed time window
            min_time_window (Optional[Union[timedelta, int]]): Minimum allowed time window
            default_time_window (Optional[Union[timedelta, int]]): Default time window if not specified
        """
        self._validate_time_windows(max_time_window, min_time_window, default_time_window)

        self.max_time_window = self._convert_to_timedelta(max_time_window)
        self.min_time_window = self._convert_to_timedelta(min_time_window)
        self.default_time_window = self._convert_to_timedelta(default_time_window)

    def _validate_time_windows(self, max_time_window, min_time_window, default_time_window):
        """
        Validate time window configurations for consistency.

        Raises:
            ValueError: If time windows are inconsistent or invalid
        """
        if max_time_window is not None and min_time_window is not None:
            max_delta = self._convert_to_timedelta(max_time_window)
            min_delta = self._convert_to_timedelta(min_time_window)
            
            if max_delta < min_delta:
                raise ValueError("Max time window must be greater than or equal to min time window")

    def _convert_to_timedelta(self, value: Optional[Union[timedelta, int]]) -> Optional[timedelta]:
        """
        Convert input to timedelta, supporting timedelta and integer inputs.

        Args:
            value (Optional[Union[timedelta, int]]): Time window value

        Returns:
            Optional[timedelta]: Converted timedelta or None
        """
        if value is None:
            return None
        
        if isinstance(value, timedelta):
            return value
        
        if isinstance(value, int):
            return timedelta(seconds=value)
        
        raise TypeError(f"Unsupported type for time window: {type(value)}")

    def get_time_window(self, requested_window: Optional[Union[timedelta, int]] = None) -> Optional[timedelta]:
        """
        Retrieve the appropriate time window, applying validation and defaults.

        Args:
            requested_window (Optional[Union[timedelta, int]]): Requested time window

        Returns:
            Optional[timedelta]: Validated time window
        """
        if requested_window is None:
            return self.default_time_window

        converted_window = self._convert_to_timedelta(requested_window)

        if self.max_time_window is not None and converted_window > self.max_time_window:
            return self.max_time_window

        if self.min_time_window is not None and converted_window < self.min_time_window:
            return self.min_time_window

        return converted_window