import secrets
import time
import uuid
from typing import Union, Dict

# Global set to track nonces across all instances
_GLOBAL_NONCE_TRACKING: Dict[str, float] = {}

class NonceService:
    """
    A service for generating and validating unique nonce (number used once) tokens.
    
    This service provides methods to:
    - Generate cryptographically secure nonces
    - Validate nonces with optional expiration
    - Track and manage nonce usage
    """
    
    def __init__(self, max_age_seconds: int = 3600):
        """
        Initialize the NonceService.
        
        Args:
            max_age_seconds (int, optional): Maximum age of a valid nonce in seconds. 
                                             Defaults to 1 hour (3600 seconds).
        """
        self._max_age = max_age_seconds
    
    def generate_nonce(self) -> str:
        """
        Generate a cryptographically secure nonce.
        
        Returns:
            str: A unique nonce token.
        """
        # Combine UUID and secure random bytes for enhanced uniqueness
        nonce = str(uuid.uuid4()) + secrets.token_hex(16)
        return nonce
    
    def validate_nonce(self, nonce: str, use_nonce: bool = True) -> bool:
        """
        Validate a nonce token.
        
        Args:
            nonce (str): The nonce to validate.
            use_nonce (bool, optional): Whether to mark the nonce as used. Defaults to True.
        
        Returns:
            bool: True if the nonce is valid and not previously used, False otherwise.
        """
        if not nonce:
            return False
        
        current_time = time.time()
        
        # Clean up expired nonces
        self._cleanup_expired_nonces(current_time)
        
        # Check if nonce has been used before
        if nonce in _GLOBAL_NONCE_TRACKING:
            return False
        
        if use_nonce:
            _GLOBAL_NONCE_TRACKING[nonce] = current_time
        
        return True
    
    def _cleanup_expired_nonces(self, current_time: float) -> None:
        """
        Remove nonces that have exceeded the maximum age.
        
        Args:
            current_time (float): Current timestamp.
        """
        global _GLOBAL_NONCE_TRACKING
        _GLOBAL_NONCE_TRACKING = {
            nonce: timestamp for nonce, timestamp in _GLOBAL_NONCE_TRACKING.items()
            if current_time - timestamp <= self._max_age
        }