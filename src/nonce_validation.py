import hashlib
import time
from typing import Dict, Any


class DistributedNonceValidator:
    """
    A distributed nonce validation service that prevents replay attacks
    and ensures unique transaction processing across distributed systems.
    """
    
    def __init__(self, expiration_time: int = 3600):
        """
        Initialize the nonce validator.
        
        :param expiration_time: Time in seconds after which a nonce expires (default: 1 hour)
        """
        self._used_nonces: Dict[str, float] = {}
        self._expiration_time = expiration_time
    
    def generate_nonce(self, context: str = '') -> str:
        """
        Generate a unique nonce for a given context.
        
        :param context: Optional context to make nonce generation more specific
        :return: A unique cryptographic nonce
        """
        # Use current timestamp and context to generate a unique hash
        timestamp = str(time.time())
        raw_nonce = f"{timestamp}:{context}"
        return hashlib.sha256(raw_nonce.encode()).hexdigest()
    
    def validate_nonce(self, nonce: str, context: str = '') -> bool:
        """
        Validate a nonce, checking for uniqueness and expiration.
        
        :param nonce: The nonce to validate
        :param context: Optional context to validate nonce against
        :return: True if nonce is valid, False otherwise
        """
        # Clean up expired nonces first
        current_time = time.time()
        self._cleanup_expired_nonces(current_time)
        
        # Check if nonce has been used before
        if nonce in self._used_nonces:
            return False
        
        # Mark nonce as used
        self._used_nonces[nonce] = current_time
        return True
    
    def _cleanup_expired_nonces(self, current_time: float) -> None:
        """
        Remove nonces that have expired.
        
        :param current_time: Current timestamp
        """
        expired_nonces = [
            nonce for nonce, timestamp in self._used_nonces.items()
            if current_time - timestamp > self._expiration_time
        ]
        
        for nonce in expired_nonces:
            del self._used_nonces[nonce]