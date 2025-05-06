import datetime
from typing import List, Callable, Any

class TransactionExpirationCleaner:
    """
    A utility class to manage and clean up expired transactions.

    This class provides methods to track transactions and remove those 
    that have exceeded a specified expiration time.
    """

    def __init__(self, expiration_time_seconds: int = 3600):
        """
        Initialize the TransactionExpirationCleaner.

        Args:
            expiration_time_seconds (int, optional): 
                Number of seconds after which a transaction is considered expired. 
                Defaults to 3600 (1 hour).
        """
        self.transactions: List[dict] = []
        self.expiration_time = expiration_time_seconds

    def add_transaction(self, transaction: Any) -> None:
        """
        Add a new transaction to be tracked.

        Args:
            transaction (Any): The transaction object to track.
        """
        transaction_entry = {
            'transaction': transaction,
            'timestamp': datetime.datetime.now()
        }
        self.transactions.append(transaction_entry)

    def clean_expired_transactions(self) -> List[Any]:
        """
        Remove and return transactions that have expired.

        A transaction is considered expired if its age exceeds the specified 
        expiration time.

        Returns:
            List[Any]: List of expired transactions that were removed.
        """
        current_time = datetime.datetime.now()
        expired_transactions = []
        
        # Filter out and remove expired transactions
        self.transactions = [
            entry for entry in self.transactions 
            if not self._is_transaction_expired(entry, current_time, expired_transactions)
        ]

        return [exp_trans['transaction'] for exp_trans in expired_transactions]

    def _is_transaction_expired(
        self, 
        transaction_entry: dict, 
        current_time: datetime.datetime, 
        expired_list: List[dict]
    ) -> bool:
        """
        Check if a transaction has expired.

        Args:
            transaction_entry (dict): The transaction entry to check.
            current_time (datetime): The current time to compare against.
            expired_list (List[dict]): List to append expired transactions to.

        Returns:
            bool: True if the transaction is expired, False otherwise.
        """
        time_diff = (current_time - transaction_entry['timestamp']).total_seconds()
        
        if time_diff > self.expiration_time:
            expired_list.append(transaction_entry)
            return True
        
        return False

    def get_current_transaction_count(self) -> int:
        """
        Get the current number of active (non-expired) transactions.

        Returns:
            int: Number of active transactions.
        """
        return len(self.transactions)