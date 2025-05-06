from typing import Any
import json
from collections import OrderedDict

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
        self._transaction_ids: OrderedDict = OrderedDict()
        self._max_cache_size = max_cache_size
    
    def _convert_to_hashable(self, transaction_id: Any) -> str:
        """
        Convert transaction ID to a unique hashable string representation.
        
        Ensures type-safe representation.
        
        Args:
            transaction_id (Any): The transaction ID to convert.
        
        Returns:
            str: A unique hashable string representation of the transaction ID.
        """
        # Create a type-specific representation
        type_prefix = type(transaction_id).__name__
        
        try:
            if isinstance(transaction_id, (list, dict, set, tuple)):
                # For complex types, use JSON serialization with sorted keys
                type_specific_id = f"{type_prefix}:{json.dumps(transaction_id, sort_keys=True)}"
            else:
                # For primitive types, use repr to capture type information
                type_specific_id = f"{type_prefix}:{repr(transaction_id)}"
            
            return type_specific_id
        except Exception:
            return f"{type_prefix}:{str(transaction_id)}"
    
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
        self._transaction_ids[hashable_id] = True
        
        # Manage cache size
        if len(self._transaction_ids) > self._max_cache_size:
            self._transaction_ids.popitem(last=False)
        
        return False
    
    def clear(self) -> None:
        """
        Clear all tracked transaction IDs.
        """
        self._transaction_ids.clear()