from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

def cleanup_expired_transactions(
    transactions: List[Dict[Any, Any]], 
    expiration_time_minutes: int = 60
) -> List[Dict[Any, Any]]:
    """
    Remove transactions that have expired based on a specified time threshold.

    Args:
        transactions (List[Dict[Any, Any]]): List of transaction dictionaries
        expiration_time_minutes (int, optional): Number of minutes after which a transaction expires. 
                                                 Defaults to 60 minutes.

    Returns:
        List[Dict[Any, Any]]: List of non-expired transactions
    
    Raises:
        ValueError: If expiration_time_minutes is not a positive integer
    """
    if not isinstance(expiration_time_minutes, int) or expiration_time_minutes <= 0:
        raise ValueError("Expiration time must be a positive integer")

    current_time = datetime.now()
    expiration_threshold = current_time - timedelta(minutes=expiration_time_minutes)

    # Keep only transactions that are not expired
    return [
        transaction for transaction in transactions
        if _is_transaction_valid(transaction, expiration_threshold)
    ]

def _is_transaction_valid(
    transaction: Dict[Any, Any], 
    expiration_threshold: datetime
) -> bool:
    """
    Check if a transaction is still valid based on its timestamp.

    Args:
        transaction (Dict[Any, Any]): Transaction dictionary
        expiration_threshold (datetime): Timestamp before which transactions are considered expired

    Returns:
        bool: True if transaction is valid, False otherwise
    """
    # Try multiple timestamp keys to accommodate different transaction formats
    timestamp_keys = ['timestamp', 'created_at', 'time']
    
    for key in timestamp_keys:
        timestamp = transaction.get(key)
        if timestamp is not None:
            # Convert timestamp to datetime if it's a string
            if isinstance(timestamp, str):
                try:
                    timestamp = datetime.fromisoformat(timestamp)
                except ValueError:
                    continue
            
            if isinstance(timestamp, datetime):
                return timestamp > expiration_threshold
    
    # If no valid timestamp is found, consider the transaction valid
    return True