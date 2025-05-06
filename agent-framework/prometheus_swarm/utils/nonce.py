import hashlib
import secrets
import time
from typing import Dict, Optional, Union

class NonceRequestInterface:
    """
    A utility class for generating and validating nonce (number used once) tokens.
    
    The nonce is a unique, cryptographically secure token used to prevent replay attacks
    and ensure the uniqueness of requests.
    """
    
    def __init__(self, max_age_seconds: int = 300):
        """
        Initialize the NonceRequestInterface.
        
        Args:
            max_age_seconds (int, optional): Maximum age of a valid nonce in seconds. 
                Defaults to 300 seconds (5 minutes).
        """
        self._nonce_store: Dict[str, float] = {}
        self._max_age = max_age_seconds
    
    def generate_nonce(self, user_id: Optional[str] = None) -> str:
        """
        Generate a unique nonce token.
        
        Args:
            user_id (Optional[str], optional): An optional user identifier to 
                include in nonce generation. Defaults to None.
        
        Returns:
            str: A unique nonce token
        """
        # Use cryptographically secure random bytes
        random_bytes = secrets.token_bytes(32)
        
        # Include current timestamp and optional user_id for additional uniqueness
        timestamp = str(time.time())
        base_string = (user_id or '') + timestamp + random_bytes.hex()
        
        # Create a SHA-256 hash of the base string
        nonce = hashlib.sha256(base_string.encode()).hexdigest()
        
        # Store the nonce with its creation timestamp
        self._nonce_store[nonce] = time.time()
        
        return nonce
    
    def validate_nonce(self, nonce: str) -> bool:
        """
        Validate a given nonce token.
        
        A nonce is valid if:
        1. It exists in the nonce store
        2. It has not exceeded the maximum age
        
        After validation, the nonce is removed to prevent reuse.
        
        Args:
            nonce (str): The nonce token to validate
        
        Returns:
            bool: True if the nonce is valid, False otherwise
        """
        # Check if nonce exists
        if nonce not in self._nonce_store:
            return False
        
        # Check nonce age
        nonce_timestamp = self._nonce_store[nonce]
        current_time = time.time()
        
        if current_time - nonce_timestamp > self._max_age:
            # Remove expired nonce
            del self._nonce_store[nonce]
            return False
        
        # Remove used nonce
        del self._nonce_store[nonce]
        return True
    
    def cleanup_expired_nonces(self) -> int:
        """
        Remove all expired nonces from the store.
        
        Returns:
            int: Number of nonces removed
        """
        current_time = time.time()
        expired_nonces = [
            nonce for nonce, timestamp in self._nonce_store.items()
            if current_time - timestamp > self._max_age
        ]
        
        for nonce in expired_nonces:
            del self._nonce_store[nonce]
        
        return len(expired_nonces)