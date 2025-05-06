import time
from typing import List, Dict, Optional
from datetime import datetime, timedelta

class NonceCleanup:
    """
    Utility class for managing and cleaning up nonces to prevent replay attacks.
    
    Manages a collection of nonces with timestamps to allow expiration and cleanup.
    """
    
    def __init__(self, expiration_time_seconds: int = 3600):
        """
        Initialize the NonceCleanup manager.
        
        :param expiration_time_seconds: Time in seconds after which a nonce is considered expired
        """
        self._nonces: Dict[str, datetime] = {}
        self._expiration_time = expiration_time_seconds
    
    def add_nonce(self, nonce: str) -> bool:
        """
        Add a new nonce to the tracking system.
        
        :param nonce: Unique nonce string to be added
        :return: True if nonce was successfully added, False if nonce already exists
        """
        if self.is_nonce_used(nonce):
            return False
        
        self._nonces[nonce] = datetime.now()
        return True
    
    def is_nonce_used(self, nonce: str) -> bool:
        """
        Check if a nonce has been previously used.
        
        :param nonce: Nonce to check
        :return: True if nonce is used, False otherwise
        """
        return nonce in self._nonces
    
    def cleanup_expired_nonces(self) -> List[str]:
        """
        Remove nonces that have exceeded the expiration time.
        
        :return: List of expired nonce strings that were removed
        """
        current_time = datetime.now()
        expired_nonces = [
            nonce for nonce, timestamp in list(self._nonces.items())
            if (current_time - timestamp).total_seconds() > self._expiration_time
        ]
        
        for nonce in expired_nonces:
            del self._nonces[nonce]
        
        return expired_nonces
    
    def get_nonce_age(self, nonce: str) -> Optional[float]:
        """
        Get the age of a specific nonce in seconds.
        
        :param nonce: Nonce to check
        :return: Age of nonce in seconds, or None if nonce doesn't exist
        """
        if nonce not in self._nonces:
            return None
        
        return (datetime.now() - self._nonces[nonce]).total_seconds()
    
    def reset(self) -> None:
        """
        Reset the nonce tracking system, clearing all stored nonces.
        """
        self._nonces.clear()