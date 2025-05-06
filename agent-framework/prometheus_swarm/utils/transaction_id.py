from typing import List, Any, Dict
from collections import defaultdict

class TransactionIDDuplicateChecker:
    """
    A utility class to check for and prevent duplicate transaction IDs.
    
    This class provides methods to:
    - Track unique transaction IDs
    - Check for duplicates
    - Reset tracking as needed
    """
    
    def __init__(self):
        """
        Initialize the duplicate checker with an empty tracking dictionary.
        """
        self._transaction_ids = defaultdict(int)
    
    def check_duplicate(self, transaction_id: str, context: str = 'default') -> bool:
        """
        Check if a transaction ID is a duplicate within a specific context.
        
        Args:
            transaction_id (str): The transaction ID to check
            context (str, optional): Scope for checking duplicate. Defaults to 'default'.
        
        Returns:
            bool: True if the transaction ID is a duplicate, False otherwise
        """
        if not isinstance(transaction_id, str):
            raise ValueError("Transaction ID must be a string")
        
        if not transaction_id:
            raise ValueError("Transaction ID cannot be empty")
        
        # If this transaction_id has been seen before in this context, it's a duplicate
        if self._transaction_ids[(context, transaction_id)] > 0:
            return True
        
        # Mark the transaction ID as seen
        self._transaction_ids[(context, transaction_id)] += 1
        return False
    
    def reset(self, context: str = None):
        """
        Reset transaction ID tracking.
        
        Args:
            context (str, optional): Specific context to reset. 
                                     If None, resets all contexts.
        """
        if context is None:
            self._transaction_ids.clear()
        else:
            # Remove only entries for the specified context
            keys_to_remove = [k for k in self._transaction_ids.keys() if k[0] == context]
            for key in keys_to_remove:
                del self._transaction_ids[key]