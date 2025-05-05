from typing import Optional
from pydantic import BaseModel, Field, validator


class TransactionIDTimeWindowConfig(BaseModel):
    """
    Configuration class for Transaction ID Time Window settings.

    Allows defining a time window for transaction ID tracking and validation.
    """
    window_size_seconds: int = Field(
        default=3600,  # Default to 1 hour
        ge=1,  # Must be at least 1 second
        le=86400,  # Maximum of 24 hours
        description="Time window size in seconds for tracking transaction IDs"
    )
    max_unique_ids: int = Field(
        default=1000,
        ge=1,  # At least 1 unique ID
        le=10000,  # Maximum of 10,000 unique IDs
        description="Maximum number of unique transaction IDs to track in the time window"
    )
    cleanup_interval_seconds: int = Field(
        default=300,  # Default to 5 minutes
        ge=60,  # Minimum cleanup every minute
        le=3600,  # Maximum cleanup every hour
        description="Interval for cleaning up expired transaction IDs"
    )

    @validator('cleanup_interval_seconds')
    def validate_cleanup_interval(cls, value, values):
        """
        Ensure cleanup interval is less than or equal to the window size.
        """
        if 'window_size_seconds' in values:
            if value > values['window_size_seconds']:
                raise ValueError("Cleanup interval must not exceed the window size")
        return value

    def get_configuration(self) -> dict:
        """
        Returns the current configuration as a dictionary.

        Returns:
            dict: A dictionary representation of the configuration
        """
        return {
            "window_size_seconds": self.window_size_seconds,
            "max_unique_ids": self.max_unique_ids,
            "cleanup_interval_seconds": self.cleanup_interval_seconds
        }