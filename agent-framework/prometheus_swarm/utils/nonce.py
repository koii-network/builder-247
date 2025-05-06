import logging
import uuid
from typing import Optional, Dict, Any
from functools import wraps
from datetime import datetime, timedelta

class NonceError(Exception):
    """Custom exception for nonce-related errors."""
    pass

class NonceManager:
    """
    Manages nonce generation, tracking, and validation.
    
    Provides mechanisms to:
    - Generate unique nonces
    - Validate nonce usage
    - Prevent replay attacks
    - Implement time-based nonce expiration
    """
    
    def __init__(
        self, 
        max_nonce_age: int = 3600,  # Default: 1 hour
        max_nonce_usage: int = 1
    ):
        """
        Initialize NonceManager with configurable parameters.
        
        Args:
            max_nonce_age (int): Maximum age of a nonce in seconds
            max_nonce_usage (int): Maximum number of times a nonce can be used
        """
        self._used_nonces: Dict[str, Dict[str, Any]] = {}
        self._max_nonce_age = max_nonce_age
        self._max_nonce_usage = max_nonce_usage
        self._logger = logging.getLogger(__name__)
    
    def generate_nonce(self) -> str:
        """
        Generate a unique nonce.
        
        Returns:
            str: A unique nonce value
        """
        nonce = str(uuid.uuid4())
        self._used_nonces[nonce] = {
            'created_at': datetime.now(),
            'usage_count': 0
        }
        return nonce
    
    def validate_nonce(self, nonce: str) -> bool:
        """
        Validate a nonce for usage.
        
        Args:
            nonce (str): Nonce to validate
        
        Returns:
            bool: Whether the nonce is valid for use
        
        Raises:
            NonceError: If nonce is invalid or expired
        """
        if nonce not in self._used_nonces:
            self._logger.warning(f"Unknown nonce: {nonce}")
            raise NonceError("Invalid nonce")
        
        nonce_info = self._used_nonces[nonce]
        
        # Check nonce age
        age = datetime.now() - nonce_info['created_at']
        if age > timedelta(seconds=self._max_nonce_age):
            del self._used_nonces[nonce]
            self._logger.warning(f"Expired nonce: {nonce}")
            raise NonceError("Nonce has expired")
        
        # Check usage count
        if nonce_info['usage_count'] >= self._max_nonce_usage:
            del self._used_nonces[nonce]
            self._logger.warning(f"Overused nonce: {nonce}")
            raise NonceError("Nonce has exceeded maximum usage")
        
        # Increment usage count
        nonce_info['usage_count'] += 1
        
        return True
    
    def cleanup_expired_nonces(self) -> int:
        """
        Remove expired nonces from tracking.
        
        Returns:
            int: Number of nonces removed
        """
        now = datetime.now()
        expired_nonces = [
            nonce for nonce, info in self._used_nonces.items()
            if now - info['created_at'] > timedelta(seconds=self._max_nonce_age)
        ]
        
        for nonce in expired_nonces:
            del self._used_nonces[nonce]
        
        return len(expired_nonces)

def nonce_protected(nonce_manager: Optional[NonceManager] = None):
    """
    Decorator to protect functions with nonce validation.
    
    Args:
        nonce_manager (Optional[NonceManager]): Nonce manager instance
    
    Returns:
        Callable: Decorated function with nonce protection
    """
    if nonce_manager is None:
        nonce_manager = NonceManager()
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, nonce: Optional[str] = None, **kwargs):
            if nonce is None:
                raise NonceError("Nonce is required")
            
            try:
                nonce_manager.validate_nonce(nonce)
                return func(*args, nonce=nonce, **kwargs)
            except NonceError as e:
                logging.error(f"Nonce validation failed: {e}")
                raise
        return wrapper
    return decorator