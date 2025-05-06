import asyncio
import uuid
from typing import Dict, List, Optional, Set

class TransactionIDManager:
    def __init__(self):
        """
        Initialize a thread-safe transaction ID management system.
        
        This class helps manage unique transaction IDs across concurrent submissions.
        """
        self._used_transaction_ids: Set[str] = set()
        self._lock = asyncio.Lock()

    async def generate_unique_transaction_id(self, max_attempts: int = 10) -> Optional[str]:
        """
        Generate a unique transaction ID with collision prevention.
        
        Args:
            max_attempts (int, optional): Maximum number of attempts to generate a unique ID. 
                                          Defaults to 10.
        
        Returns:
            Optional[str]: A unique transaction ID, or None if unable to generate after max attempts.
        """
        for _ in range(max_attempts):
            async with self._lock:
                # Generate a new UUID
                new_transaction_id = str(uuid.uuid4())
                
                # Check if the ID is already used
                if new_transaction_id not in self._used_transaction_ids:
                    return new_transaction_id
        
        return None

    async def submit_transaction(self, transaction_id: str) -> bool:
        """
        Submit a transaction with first-writer-wins concurrency strategy.
        
        This method ensures that only the first concurrent submission is successful.
        
        Args:
            transaction_id (str): The transaction ID to submit.
        
        Returns:
            bool: True if the transaction was first to be submitted, False otherwise.
        """
        async with self._lock:
            # First check: if transaction already exists, return False
            if transaction_id in self._used_transaction_ids:
                return False
            
            # Second check: this ensures first-writer-wins
            self._used_transaction_ids.add(transaction_id)
            return True

    async def reset_transactions(self):
        """
        Reset all tracked transaction IDs.
        
        Useful for testing or clearing state between test scenarios.
        """
        async with self._lock:
            self._used_transaction_ids.clear()