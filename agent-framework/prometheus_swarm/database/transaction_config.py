from typing import Dict, Any, Optional

class TransactionIDRetentionConfig:
    """
    Configuration class for managing transaction ID retention settings.
    
    This class provides methods to configure and retrieve retention policies
    for transaction IDs, including settings like maximum retention time,
    maximum number of stored IDs, and cleanup strategies.
    """
    
    def __init__(self, 
                 max_retention_time: Optional[int] = 86400,  # 24 hours default
                 max_stored_ids: Optional[int] = 1000,
                 retention_strategy: Optional[str] = 'oldest'):
        """
        Initialize Transaction ID Retention Configuration.
        
        Args:
            max_retention_time (int, optional): Maximum time (in seconds) 
                transaction IDs are kept. Defaults to 24 hours.
            max_stored_ids (int, optional): Maximum number of transaction 
                IDs to store. Defaults to 1000.
            retention_strategy (str, optional): Strategy for managing 
                transaction IDs when limit is reached. 
                Options: 'oldest' (remove oldest), 'newest' (remove newest).
                Defaults to 'oldest'.
        """
        self._config: Dict[str, Any] = {
            'max_retention_time': max(0, max_retention_time or 86400),
            'max_stored_ids': max(1, max_stored_ids or 1000),
            'retention_strategy': retention_strategy or 'oldest'
        }
    
    def get_config(self) -> Dict[str, Any]:
        """
        Retrieve the current transaction ID retention configuration.
        
        Returns:
            Dict[str, Any]: Current configuration settings.
        """
        return self._config.copy()
    
    def update_config(self, 
                      max_retention_time: Optional[int] = None,
                      max_stored_ids: Optional[int] = None,
                      retention_strategy: Optional[str] = None) -> None:
        """
        Update the transaction ID retention configuration.
        
        Args:
            max_retention_time (int, optional): New maximum retention time.
            max_stored_ids (int, optional): New maximum number of stored IDs.
            retention_strategy (str, optional): New retention strategy.
        
        Raises:
            ValueError: If an invalid retention strategy is provided.
        """
        if retention_strategy and retention_strategy not in ['oldest', 'newest']:
            raise ValueError("Retention strategy must be 'oldest' or 'newest'")
        
        if max_retention_time is not None:
            self._config['max_retention_time'] = max(0, max_retention_time)
        
        if max_stored_ids is not None:
            self._config['max_stored_ids'] = max(1, max_stored_ids)
        
        if retention_strategy is not None:
            self._config['retention_strategy'] = retention_strategy