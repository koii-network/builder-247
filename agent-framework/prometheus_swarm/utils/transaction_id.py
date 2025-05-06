import threading
from typing import Dict, Any, Optional
from uuid import uuid4

class TransactionIDManager:
    """
    Thread-safe manager for generating and tracking transaction IDs.
    
    This class provides concurrent-safe methods for:
    - Generating unique transaction IDs
    - Tracking transaction status
    - Handling concurrent transaction submissions
    """
    
    def __init__(self):
        """
        Initialize the TransactionIDManager with thread-safe mechanisms.
        """
        self._transactions: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()
    
    def generate_transaction_id(self) -> str:
        """
        Generate a unique transaction ID.
        
        Returns:
            str: A unique transaction identifier
        """
        return str(uuid4())
    
    def submit_transaction(self, data: Dict[str, Any]) -> str:
        """
        Submit a transaction with thread-safety.
        
        Args:
            data (Dict[str, Any]): Transaction data to be submitted
        
        Returns:
            str: Generated transaction ID
        """
        transaction_id = self.generate_transaction_id()
        
        with self._lock:
            self._transactions[transaction_id] = {
                'data': data,
                'status': 'pending',
                'timestamp': threading.get_ident()
            }
        
        return transaction_id
    
    def get_transaction_status(self, transaction_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve transaction status with thread-safety.
        
        Args:
            transaction_id (str): ID of the transaction to retrieve
        
        Returns:
            Optional[Dict[str, Any]]: Transaction details or None if not found
        """
        with self._lock:
            return self._transactions.get(transaction_id)
    
    def update_transaction_status(self, transaction_id: str, status: str) -> bool:
        """
        Update transaction status with thread-safety.
        
        Args:
            transaction_id (str): ID of the transaction to update
            status (str): New status for the transaction
        
        Returns:
            bool: True if update successful, False if transaction not found
        """
        with self._lock:
            if transaction_id in self._transactions:
                self._transactions[transaction_id]['status'] = status
                return True
            return False