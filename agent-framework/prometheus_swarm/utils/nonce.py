import uuid
import time
import hashlib
from typing import Dict, Any, Optional

class NonceRequestInterface:
    """
    A class to manage nonce (number used once) requests for secure communication.
    
    The nonce is a unique, one-time use value that helps prevent replay attacks
    and ensures the uniqueness of each request.
    """
    
    def __init__(self, max_age_seconds: int = 300):
        """
        Initialize the Nonce Request Interface.
        
        :param max_age_seconds: Maximum time a nonce is considered valid (default 5 minutes)
        """
        self._nonce_store: Dict[str, Dict[str, Any]] = {}
        self._max_age_seconds = max_age_seconds
    
    def generate_nonce(self, context: Optional[str] = None) -> str:
        """
        Generate a unique nonce.
        
        :param context: Optional context for the nonce (e.g., user ID, request type)
        :return: A unique nonce string
        """
        # Generate a UUID-based nonce
        nonce = str(uuid.uuid4())
        
        # Store nonce details
        self._nonce_store[nonce] = {
            'created_at': time.time(),
            'context': context,
            'used': False
        }
        
        return nonce
    
    def validate_nonce(self, nonce: str, context: Optional[str] = None) -> bool:
        """
        Validate a nonce.
        
        :param nonce: Nonce to validate
        :param context: Optional context to match against
        :return: True if nonce is valid, False otherwise
        """
        # Check if nonce exists
        if nonce not in self._nonce_store:
            return False
        
        # Get nonce details
        nonce_details = self._nonce_store[nonce]
        
        # Check if nonce has already been used
        if nonce_details['used']:
            return False
        
        # Check nonce age
        current_time = time.time()
        if current_time - nonce_details['created_at'] > self._max_age_seconds:
            del self._nonce_store[nonce]
            return False
        
        # Check context if provided
        if context is not None and nonce_details['context'] != context:
            return False
        
        # Mark nonce as used
        nonce_details['used'] = True
        
        return True
    
    def clear_expired_nonces(self) -> int:
        """
        Clear expired nonces from the store.
        
        :return: Number of nonces removed
        """
        current_time = time.time()
        expired_nonces = [
            nonce for nonce, details in self._nonce_store.items()
            if details['used'] or current_time - details['created_at'] > self._max_age_seconds
        ]
        
        for nonce in expired_nonces:
            del self._nonce_store[nonce]
        
        return len(expired_nonces)