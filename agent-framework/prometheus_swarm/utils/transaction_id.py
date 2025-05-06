from typing import Set, Any
from functools import lru_cache

class TransactionIDManager:
    """
    A utility class to manage and check for transaction ID duplications.
    
    This class provides thread-safe mechanisms to track and validate transaction IDs,
    preventing duplicate processing of transactions.
    """
    
    def __init__(self, max_cache_size: int = 1000):
        """
        Initialize the TransactionIDManager.
        
        Args:
            max_cache_size (int, optional): Maximum number of transaction IDs to cache. 
                Defaults to 1000.
        """
        self._transaction_ids: Set[Any] = set()
        self._max_cache_size = max_cache_size
    
    def is_duplicate(self, transaction_id: Any) -> bool:
        """
        Check if a transaction ID is a duplicate.
        
        Args:
            transaction_id (Any): The transaction ID to check.
        
        Returns:
            bool: True if the transaction ID is a duplicate, False otherwise.
        """
        if transaction_id in self._transaction_ids:
            return True
        
        # Add new transaction ID and manage cache size
        self._transaction_ids.add(transaction_id)
        
        if len(self._transaction_ids) > self._max_cache_size:
            # Remove oldest transaction ID to prevent unbounded growth
            oldest_id = next(iter(self._transaction_ids))
            self._transaction_ids.remove(oldest_id)
        
        return False
    
    def clear(self) -> None:
        """
        Clear all tracked transaction IDs.
        """
        self._transaction_ids.clear()