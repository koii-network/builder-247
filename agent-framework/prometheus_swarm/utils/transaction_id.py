from typing import Set, Any, Hashable
from functools import lru_cache
import json

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
        self._transaction_ids: Set[str] = set()
        self._max_cache_size = max_cache_size
        self._order_of_entry = []
    
    def _convert_to_hashable(self, transaction_id: Any) -> str:
        """
        Convert transaction ID to a hashable string representation.
        
        Args:
            transaction_id (Any): The transaction ID to convert.
        
        Returns:
            str: A hashable string representation of the transaction ID.
        """
        try:
            # Try direct string conversion first
            return str(transaction_id)
        except Exception:
            # Fallback to JSON serialization for complex types
            return json.dumps(transaction_id, sort_keys=True)
    
    def is_duplicate(self, transaction_id: Any) -> bool:
        """
        Check if a transaction ID is a duplicate.
        
        Args:
            transaction_id (Any): The transaction ID to check.
        
        Returns:
            bool: True if the transaction ID is a duplicate, False otherwise.
        """
        hashable_id = self._convert_to_hashable(transaction_id)
        
        # Check for duplicate
        if hashable_id in self._transaction_ids:
            return True
        
        # Add new transaction ID
        self._transaction_ids.add(hashable_id)
        self._order_of_entry.append(hashable_id)
        
        # Manage cache size
        if len(self._transaction_ids) > self._max_cache_size:
            oldest_id = self._order_of_entry.pop(0)
            self._transaction_ids.remove(oldest_id)
        
        return False
    
    def clear(self) -> None:
        """
        Clear all tracked transaction IDs.
        """
        self._transaction_ids.clear()
        self._order_of_entry.clear()