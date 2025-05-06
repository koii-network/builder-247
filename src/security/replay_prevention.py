import time
from typing import Dict, Any
from functools import wraps

class ReplayAttackPrevention:
    """
    A class to implement replay attack prevention mechanisms.
    
    This class provides methods to validate and track unique transactions
    to prevent replay attacks by maintaining a record of processed transactions.
    """
    
    def __init__(self, max_timestamp_drift_seconds: int = 300, max_nonce_history: int = 1000):
        """
        Initialize replay attack prevention settings.
        
        Args:
            max_timestamp_drift_seconds (int): Maximum allowed time difference 
                between message timestamp and current time. Defaults to 5 minutes.
            max_nonce_history (int): Maximum number of nonces to keep track of. 
                Prevents memory growth. Defaults to 1000.
        """
        self._nonce_history: Dict[str, float] = {}
        self._max_timestamp_drift = max_timestamp_drift_seconds
        self._max_nonce_history = max_nonce_history
    
    def validate_transaction(self, nonce: str, timestamp: float = None) -> bool:
        """
        Validate a transaction to prevent replay attacks.
        
        Args:
            nonce (str): A unique identifier for the transaction.
            timestamp (float, optional): Timestamp of the transaction. 
                Defaults to current time if not provided.
        
        Returns:
            bool: Whether the transaction is valid and unique.
        """
        current_time = time.time()
        timestamp = timestamp or current_time
        
        # Check timestamp drift
        if abs(current_time - timestamp) > self._max_timestamp_drift:
            return False
        
        # Check nonce uniqueness
        if nonce in self._nonce_history:
            return False
        
        # Store nonce and clean up old entries
        self._nonce_history[nonce] = current_time
        self._clean_nonce_history()
        
        return True
    
    def _clean_nonce_history(self):
        """
        Clean up old nonce entries to prevent memory growth.
        Removes entries older than max timestamp drift and 
        trims history if it exceeds max nonce history size.
        """
        current_time = time.time()
        self._nonce_history = {
            k: v for k, v in self._nonce_history.items() 
            if current_time - v <= self._max_timestamp_drift
        }
        
        # If history is too large, keep the most recent entries
        if len(self._nonce_history) > self._max_nonce_history:
            sorted_entries = sorted(
                self._nonce_history.items(), 
                key=lambda x: x[1], 
                reverse=True
            )
            self._nonce_history = dict(sorted_entries[:self._max_nonce_history])
    
    def transaction_decorator(self, func):
        """
        A decorator to automatically prevent replay attacks for a function.
        
        Args:
            func (callable): The function to protect against replay attacks.
        
        Returns:
            callable: A wrapped function with replay attack prevention.
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Attempt to extract nonce from kwargs, with fallback
            nonce = kwargs.get('replay_nonce')
            if not nonce:
                raise ValueError("No nonce provided for replay attack prevention")
            
            # Validate transaction before executing
            if not self.validate_transaction(nonce):
                raise ValueError("Potential replay attack detected")
            
            return func(*args, **kwargs)
        return wrapper