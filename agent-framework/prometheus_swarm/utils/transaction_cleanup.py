from typing import List, Dict, Any
from datetime import datetime, timedelta

class TransactionCleanupError(Exception):
    """Custom exception for transaction cleanup errors."""
    pass

def cleanup_expired_transactions(
    transactions: List[Dict[Any, Any]], 
    expiration_hours: int = 24
) -> List[Dict[Any, Any]]:
    """
    Clean up expired transactions based on a specified expiration time.

    Args:
        transactions (List[Dict]): List of transaction dictionaries.
        expiration_hours (int, optional): Hours after which a transaction is considered expired. 
                                          Defaults to 24 hours.

    Returns:
        List[Dict]: List of non-expired transactions.

    Raises:
        TransactionCleanupError: If input is invalid.
    """
    if not isinstance(transactions, list):
        raise TransactionCleanupError("Transactions must be a list")
    
    if not isinstance(expiration_hours, int) or expiration_hours <= 0:
        raise TransactionCleanupError("Expiration hours must be a positive integer")
    
    current_time = datetime.now()
    
    try:
        non_expired_transactions = [
            transaction for transaction in transactions
            if _is_transaction_valid(transaction, current_time, expiration_hours)
        ]
        
        return non_expired_transactions
    
    except Exception as e:
        raise TransactionCleanupError(f"Error during transaction cleanup: {e}")

def _is_transaction_valid(
    transaction: Dict[Any, Any], 
    current_time: datetime, 
    expiration_hours: int
) -> bool:
    """
    Check if a transaction is valid based on its timestamp.

    Args:
        transaction (Dict): Transaction dictionary.
        current_time (datetime): Current timestamp.
        expiration_hours (int): Hours after which transaction expires.

    Returns:
        bool: True if transaction is valid, False otherwise.
    """
    if not isinstance(transaction, dict):
        return False
    
    # Assuming transaction has a 'timestamp' key
    timestamp_str = transaction.get('timestamp')
    
    if not timestamp_str:
        return False
    
    try:
        transaction_time = datetime.fromisoformat(timestamp_str)
        expiration_time = transaction_time + timedelta(hours=expiration_hours)
        
        return current_time <= expiration_time
    
    except (ValueError, TypeError):
        return False