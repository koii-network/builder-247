from typing import Optional, Dict, Any
from dataclasses import dataclass, field

@dataclass
class TransactionIDTimeWindowConfig:
    """
    Configuration class for Transaction ID Time Window settings.
    
    Attributes:
        window_duration (int): Duration of the time window in seconds.
        max_transactions (Optional[int]): Maximum number of transactions allowed in the window.
        cleanup_interval (int): Interval for cleaning up expired transaction entries.
        enabled (bool): Flag to enable or disable transaction ID time window tracking.
        additional_config (Dict[str, Any]): Additional configuration options.
    """
    window_duration: int = 3600  # Default 1 hour
    max_transactions: Optional[int] = None  # No limit by default
    cleanup_interval: int = 300  # Default 5 minutes
    enabled: bool = True
    additional_config: Dict[str, Any] = field(default_factory=dict)

    def validate(self) -> bool:
        """
        Validate the configuration settings.
        
        Returns:
            bool: True if configuration is valid, False otherwise.
        """
        if self.window_duration <= 0:
            return False
        
        if self.max_transactions is not None and self.max_transactions <= 0:
            return False
        
        if self.cleanup_interval <= 0:
            return False
        
        return True

    def get_config(self) -> Dict[str, Any]:
        """
        Get the full configuration as a dictionary.
        
        Returns:
            Dict[str, Any]: Configuration dictionary.
        """
        return {
            "window_duration": self.window_duration,
            "max_transactions": self.max_transactions,
            "cleanup_interval": self.cleanup_interval,
            "enabled": self.enabled,
            **self.additional_config
        }