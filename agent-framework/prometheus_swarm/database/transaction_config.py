from typing import Optional, Union
from dataclasses import dataclass, field

@dataclass
class TransactionIDRetentionConfig:
    """
    Configuration class for Transaction ID retention settings.

    Attributes:
        max_retention_count (int): Maximum number of transaction IDs to retain.
        max_retention_days (Optional[int]): Maximum number of days to retain transaction IDs.
        enable_cleanup (bool): Flag to enable automatic cleanup of transaction IDs.
        priority_preserve_types (list[str]): List of transaction types to prioritize for retention.
    """
    max_retention_count: int = 1000
    max_retention_days: Optional[int] = None
    enable_cleanup: bool = True
    priority_preserve_types: list[str] = field(default_factory=list)

    def validate(self) -> bool:
        """
        Validate the transaction ID retention configuration.

        Returns:
            bool: True if configuration is valid, False otherwise.
        """
        if self.max_retention_count < 0:
            return False
        
        if self.max_retention_days is not None and self.max_retention_days < 0:
            return False
        
        return True

    def get_retention_limit(self) -> Union[int, None]:
        """
        Get the effective retention limit.

        Returns:
            Union[int, None]: Maximum number of transaction IDs to retain or None if no limit.
        """
        return self.max_retention_count if self.enable_cleanup else None

def create_default_transaction_config() -> TransactionIDRetentionConfig:
    """
    Create a default transaction ID retention configuration.

    Returns:
        TransactionIDRetentionConfig: Default configuration instance.
    """
    return TransactionIDRetentionConfig()