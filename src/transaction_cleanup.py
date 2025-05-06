import datetime
from typing import List, Optional

class TransactionIdCleanupJob:
    """
    Background job for cleaning up transaction IDs based on specified criteria.
    
    This class provides functionality to remove outdated or expired transaction IDs 
    from a collection, helping manage system resources and prevent database bloat.
    """
    
    @staticmethod
    def cleanup_transaction_ids(
        transactions: List[dict], 
        max_age_days: int = 30, 
        current_time: Optional[datetime.datetime] = None
    ) -> List[dict]:
        """
        Clean up transaction IDs that are older than the specified max age.
        
        Args:
            transactions (List[dict]): List of transaction dictionaries
            max_age_days (int, optional): Maximum age of transactions to keep. Defaults to 30.
            current_time (datetime.datetime, optional): Current time for testing purposes
        
        Returns:
            List[dict]: Filtered list of recent transactions
        
        Raises:
            ValueError: If max_age_days is negative
        """
        if max_age_days < 0:
            raise ValueError("Max age days must be non-negative")
        
        # Use provided current time or get current time
        now = current_time or datetime.datetime.now()
        
        # Filter out transactions older than max_age_days
        recent_transactions = [
            transaction for transaction in transactions
            if (now - transaction.get('timestamp', now)).days < max_age_days
        ]
        
        return recent_transactions