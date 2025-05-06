from typing import Union, Optional
from dataclasses import dataclass

@dataclass
class TransactionIdRetentionConfig:
    """
    Configuration class for Transaction ID retention settings.
    
    Attributes:
        max_retention_days (int): Maximum number of days to retain transaction IDs.
        max_transaction_count (Optional[int]): Maximum number of transactions to retain.
        enabled (bool): Flag to enable or disable transaction ID retention.
    """
    
    max_retention_days: int = 30
    max_transaction_count: Optional[int] = None
    enabled: bool = True
    
    def __post_init__(self):
        """
        Validate configuration parameters after initialization.
        
        Raises:
            ValueError: If configuration parameters are invalid.
        """
        if self.max_retention_days <= 0:
            raise ValueError("max_retention_days must be a positive integer")
        
        if self.max_transaction_count is not None and self.max_transaction_count <= 0:
            raise ValueError("max_transaction_count must be a positive integer or None")

def create_transaction_id_config(
    max_retention_days: int = 30,
    max_transaction_count: Optional[int] = None,
    enabled: bool = True
) -> TransactionIdRetentionConfig:
    """
    Create a TransactionIdRetentionConfig instance with optional customization.
    
    Args:
        max_retention_days (int, optional): Maximum days to retain transaction IDs. Defaults to 30.
        max_transaction_count (Optional[int], optional): Maximum transactions to retain. Defaults to None.
        enabled (bool, optional): Enable transaction ID retention. Defaults to True.
    
    Returns:
        TransactionIdRetentionConfig: Configured transaction ID retention settings.
    """
    return TransactionIdRetentionConfig(
        max_retention_days=max_retention_days,
        max_transaction_count=max_transaction_count,
        enabled=enabled
    )