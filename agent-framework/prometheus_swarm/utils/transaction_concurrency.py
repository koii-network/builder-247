import threading
from typing import List, Optional, Dict
from uuid import uuid4

class TransactionIDManager:
    """
    A thread-safe manager for generating and tracking unique transaction IDs.
    
    This class ensures that:
    1. Each transaction ID is unique 
    2. Concurrent transactions can be safely handled
    3. Proper tracking of transaction states
    """
    
    def __init__(self):
        """
        Initialize the TransactionIDManager with thread-safe mechanisms.
        """
        self._lock = threading.Lock()
        self._transactions: Dict[str, str] = {}
    
    def generate_transaction_id(self) -> str:
        """
        Generates a unique transaction ID in a thread-safe manner.
        
        Returns:
            str: A unique transaction ID
        """
        with self._lock:
            # Use UUID4 to ensure high probability of uniqueness
            transaction_id = str(uuid4())
            return transaction_id
    
    def register_transaction(self, transaction_id: str, state: str = 'pending') -> bool:
        """
        Register a transaction with an optional initial state.
        
        Args:
            transaction_id (str): The transaction ID to register
            state (str, optional): Initial state of the transaction. Defaults to 'pending'
        
        Returns:
            bool: True if registration was successful, False if transaction already exists
        """
        with self._lock:
            if transaction_id in self._transactions:
                return False
            
            self._transactions[transaction_id] = state
            return True
    
    def update_transaction_state(self, transaction_id: str, new_state: str) -> bool:
        """
        Update the state of a specific transaction.
        
        Args:
            transaction_id (str): The transaction ID to update
            new_state (str): The new state for the transaction
        
        Returns:
            bool: True if state was successfully updated, False if transaction not found
        """
        with self._lock:
            if transaction_id not in self._transactions:
                return False
            
            self._transactions[transaction_id] = new_state
            return True
    
    def get_transaction_state(self, transaction_id: str) -> Optional[str]:
        """
        Retrieve the current state of a transaction.
        
        Args:
            transaction_id (str): The transaction ID to check
        
        Returns:
            Optional[str]: The current state of the transaction, or None if not found
        """
        with self._lock:
            return self._transactions.get(transaction_id)
    
    def complete_transaction(self, transaction_id: str) -> bool:
        """
        Mark a transaction as complete.
        
        Args:
            transaction_id (str): The transaction ID to complete
        
        Returns:
            bool: True if transaction was successfully completed, False if not found
        """
        return self.update_transaction_state(transaction_id, 'completed')
    
    def reset(self):
        """
        Reset the entire transaction tracking system.
        Useful for testing or resetting the state.
        """
        with self._lock:
            self._transactions.clear()