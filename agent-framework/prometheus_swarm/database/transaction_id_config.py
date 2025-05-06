from typing import Optional, Union
from dataclasses import dataclass, field
from datetime import timedelta

@dataclass
class TransactionIdRetentionConfig:
    """
    Configuration for transaction ID retention settings.
    
    Attributes:
        max_retention_period (Optional[timedelta]): Maximum time to retain transaction IDs.
        max_transaction_count (Optional[int]): Maximum number of transaction IDs to retain.
        enabled (bool): Whether transaction ID retention is enabled.
    """
    max_retention_period: Optional[timedelta] = None
    max_transaction_count: Optional[int] = None
    enabled: bool = True

    def __post_init__(self):
        """
        Validate configuration parameters after initialization.
        """
        if self.max_retention_period is not None and not isinstance(self.max_retention_period, timedelta):
            raise TypeError("max_retention_period must be a timedelta object")
        
        if self.max_transaction_count is not None:
            if not isinstance(self.max_transaction_count, int):
                raise TypeError("max_transaction_count must be an integer")
            if self.max_transaction_count < 0:
                raise ValueError("max_transaction_count must be non-negative")

def create_transaction_id_retention_config(
    max_retention_period: Optional[Union[timedelta, int]] = None,
    max_transaction_count: Optional[int] = None,
    enabled: bool = True
) -> TransactionIdRetentionConfig:
    """
    Factory function to create a TransactionIdRetentionConfig with optional validations.
    
    Args:
        max_retention_period (Optional[Union[timedelta, int]]): Maximum retention period.
                         If int is provided, it's interpreted as days.
        max_transaction_count (Optional[int]): Maximum number of transaction IDs to retain.
        enabled (bool): Whether transaction ID retention is enabled.
    
    Returns:
        TransactionIdRetentionConfig: Configured retention settings.
    
    Raises:
        TypeError: If input types are incorrect.
        ValueError: If input values are invalid.
    """
    if isinstance(max_retention_period, int):
        max_retention_period = timedelta(days=max_retention_period)
    
    return TransactionIdRetentionConfig(
        max_retention_period=max_retention_period,
        max_transaction_count=max_transaction_count,
        enabled=enabled
    )