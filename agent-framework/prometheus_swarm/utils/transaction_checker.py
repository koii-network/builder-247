from typing import List, Dict, Any

class TransactionDuplicationChecker:
    """
    A utility class to check for transaction ID duplication.
    
    This class provides methods to detect and prevent duplicate transaction IDs
    across different transactions or within a specific context.
    """
    
    def __init__(self):
        """
        Initialize the transaction duplication checker.
        
        Uses an internal set to track unique transaction IDs.
        """
        self._transaction_ids = set()
    
    def is_duplicate(self, transaction_id: str) -> bool:
        """
        Check if a transaction ID is a duplicate.
        
        Args:
            transaction_id (str): The transaction ID to check for duplication.
        
        Returns:
            bool: True if the transaction ID is a duplicate, False otherwise.
        """
        return transaction_id in self._transaction_ids
    
    def add_transaction(self, transaction_id: str) -> bool:
        """
        Add a transaction ID and check for duplication.
        
        Args:
            transaction_id (str): The transaction ID to add.
        
        Returns:
            bool: True if the transaction ID is unique (not a duplicate), 
                  False if it's a duplicate.
        """
        if self.is_duplicate(transaction_id):
            return False
        
        self._transaction_ids.add(transaction_id)
        return True
    
    def clear(self) -> None:
        """
        Clear all tracked transaction IDs.
        """
        self._transaction_ids.clear()
    
    def get_unique_transactions(self, transactions: List[Dict[str, Any]], 
                                id_key: str = 'transaction_id') -> List[Dict[str, Any]]:
        """
        Filter out duplicate transactions from a list.
        
        Args:
            transactions (List[Dict[str, Any]]): List of transaction dictionaries.
            id_key (str, optional): Key to use for transaction ID. Defaults to 'transaction_id'.
        
        Returns:
            List[Dict[str, Any]]: List of unique transactions.
        """
        unique_transactions = []
        for transaction in transactions:
            transaction_id = transaction.get(id_key)
            
            if transaction_id is None:
                # If no transaction ID, include the transaction
                unique_transactions.append(transaction)
                continue
            
            if self.add_transaction(transaction_id):
                unique_transactions.append(transaction)
        
        return unique_transactions