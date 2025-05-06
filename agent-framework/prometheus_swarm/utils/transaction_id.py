from typing import Set, Any

class TransactionIDChecker:
    """
    A utility class to check for transaction ID duplication.
    
    This class provides methods to track and check unique transaction IDs
    to prevent duplicate processing.
    """
    
    def __init__(self):
        """
        Initialize the TransactionIDChecker with an empty set of transaction IDs.
        """
        self._transaction_ids: Set[Any] = set()
    
    def is_duplicate(self, transaction_id: Any) -> bool:
        """
        Check if a given transaction ID is a duplicate.
        
        Args:
            transaction_id (Any): The transaction ID to check for duplication.
        
        Returns:
            bool: True if the transaction ID is a duplicate, False otherwise.
        
        Raises:
            TypeError: If the transaction_id is None.
        """
        if transaction_id is None:
            raise TypeError("Transaction ID cannot be None")
        
        return transaction_id in self._transaction_ids
    
    def add_transaction_id(self, transaction_id: Any) -> None:
        """
        Add a transaction ID to the tracked set.
        
        Args:
            transaction_id (Any): The transaction ID to add.
        
        Raises:
            TypeError: If the transaction_id is None.
            ValueError: If the transaction ID is already present.
        """
        if transaction_id is None:
            raise TypeError("Transaction ID cannot be None")
        
        if self.is_duplicate(transaction_id):
            raise ValueError(f"Duplicate transaction ID: {transaction_id}")
        
        self._transaction_ids.add(transaction_id)
    
    def clear(self) -> None:
        """
        Clear all tracked transaction IDs.
        """
        self._transaction_ids.clear()
    
    def get_tracked_count(self) -> int:
        """
        Get the number of tracked transaction IDs.
        
        Returns:
            int: The number of unique transaction IDs tracked.
        """
        return len(self._transaction_ids)