from typing import List, Any, Dict

class TransactionIdChecker:
    """
    A utility class to check for transaction ID duplication.
    
    This class provides methods to detect and prevent duplicate transaction IDs
    in a collection of transactions.
    """
    
    @staticmethod
    def check_duplicates(transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Check for duplicate transaction IDs in a list of transactions.
        
        Args:
            transactions (List[Dict[str, Any]]): A list of transaction dictionaries.
        
        Returns:
            List[Dict[str, Any]]: A list of duplicated transactions.
        
        Raises:
            ValueError: If any transaction is missing a transaction ID.
        """
        if not transactions:
            return []
        
        # Validate that each transaction has a transaction ID
        for transaction in transactions:
            if 'transaction_id' not in transaction:
                raise ValueError("Transaction is missing 'transaction_id' key")
        
        # Find duplicate transaction IDs
        seen_ids = set()
        duplicates = []
        
        for transaction in transactions:
            transaction_id = transaction['transaction_id']
            
            if transaction_id in seen_ids:
                duplicates.append(transaction)
            else:
                seen_ids.add(transaction_id)
        
        return duplicates
    
    @staticmethod
    def ensure_unique_transactions(transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Ensure transactions have unique transaction IDs by removing duplicates.
        
        Args:
            transactions (List[Dict[str, Any]]): A list of transaction dictionaries.
        
        Returns:
            List[Dict[str, Any]]: A list of transactions with unique transaction IDs.
        
        Raises:
            ValueError: If any transaction is missing a transaction ID.
        """
        if not transactions:
            return []
        
        # Validate that each transaction has a transaction ID
        for transaction in transactions:
            if 'transaction_id' not in transaction:
                raise ValueError("Transaction is missing 'transaction_id' key")
        
        # Remove duplicates while preserving order
        seen_ids = set()
        unique_transactions = []
        
        for transaction in transactions:
            transaction_id = transaction['transaction_id']
            
            if transaction_id not in seen_ids:
                unique_transactions.append(transaction)
                seen_ids.add(transaction_id)
        
        return unique_transactions