import time
from typing import Dict, Any
import hashlib
import threading

class NonceTracker:
    """
    A thread-safe nonce tracking mechanism to prevent replay attacks and duplicate requests.
    
    Features:
    - Tracks used nonces with an optional expiration time
    - Thread-safe using threading.Lock()
    - Configurable nonce lifetime
    """
    
    def __init__(self, max_nonce_lifetime: int = 3600):
        """
        Initialize the NonceTracker.
        
        :param max_nonce_lifetime: Maximum time (in seconds) a nonce is considered valid. Default is 1 hour.
        """
        self._used_nonces: Dict[str, float] = {}
        self._lock = threading.Lock()
        self._max_nonce_lifetime = max_nonce_lifetime
    
    def generate_nonce(self, data: Any = None) -> str:
        """
        Generate a unique nonce based on current timestamp and optional data.
        
        :param data: Optional additional data to include in nonce generation
        :return: A unique nonce string
        """
        current_time = time.time()
        
        # Include current time and optional data in nonce generation
        nonce_input = f"{current_time}:{str(data)}"
        
        # Create a hash to generate a unique nonce
        nonce = hashlib.sha256(nonce_input.encode()).hexdigest()
        
        # Store the nonce with its creation timestamp
        with self._lock:
            self._used_nonces[nonce] = current_time
        
        return nonce
    
    def validate_nonce(self, nonce: str) -> bool:
        """
        Validate if a nonce is unique and not expired.
        
        :param nonce: Nonce to validate
        :return: True if nonce is valid, False otherwise
        """
        current_time = time.time()
        
        with self._lock:
            # Check if nonce exists and is not expired
            if nonce not in self._used_nonces:
                return False
            
            nonce_timestamp = self._used_nonces[nonce]
            
            # Check if nonce has expired
            if current_time - nonce_timestamp > self._max_nonce_lifetime:
                del self._used_nonces[nonce]
                return False
            
            return True
    
    def remove_expired_nonces(self) -> None:
        """
        Remove nonces that have exceeded the maximum lifetime.
        This method can be called periodically to clean up old nonces.
        """
        current_time = time.time()
        
        with self._lock:
            # Create a list of expired nonce keys
            expired_nonces = [
                nonce for nonce, timestamp in self._used_nonces.items()
                if current_time - timestamp > self._max_nonce_lifetime
            ]
            
            # Remove expired nonces
            for nonce in expired_nonces:
                del self._used_nonces[nonce]