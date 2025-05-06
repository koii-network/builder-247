from typing import Dict, Any, Optional
import uuid
import time
from datetime import datetime, timedelta

class NonceRequest:
    """
    A class to manage cryptographic nonce requests with expiration and validation.
    
    Nonces are one-time tokens used to prevent replay attacks and ensure request uniqueness.
    """
    
    def __init__(self, 
                 duration: int = 300,  # Default 5 minutes
                 allow_reuse: bool = False):
        """
        Initialize a NonceRequest manager.
        
        Args:
            duration (int): How long a nonce remains valid in seconds. Defaults to 300 (5 minutes).
            allow_reuse (bool): Whether nonces can be reused. Defaults to False.
        """
        self._nonces: Dict[str, Dict[str, Any]] = {}
        self._duration = duration
        self._allow_reuse = allow_reuse
    
    def generate_nonce(self, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate a new unique nonce.
        
        Args:
            context (dict, optional): Additional context to associate with the nonce.
        
        Returns:
            str: A unique nonce token
        """
        nonce = str(uuid.uuid4())
        expiration = datetime.now() + timedelta(seconds=self._duration)
        
        self._nonces[nonce] = {
            'created_at': datetime.now(),
            'expires_at': expiration,
            'context': context or {},
            'used': False
        }
        
        return nonce
    
    def validate_nonce(self, nonce: str) -> bool:
        """
        Validate a given nonce.
        
        Args:
            nonce (str): The nonce to validate
        
        Returns:
            bool: Whether the nonce is valid and usable
        """
        if nonce not in self._nonces:
            return False
        
        nonce_info = self._nonces[nonce]
        
        # Check expiration
        if datetime.now() > nonce_info['expires_at']:
            return False
        
        # Check reuse
        if not self._allow_reuse and nonce_info['used']:
            return False
        
        # Mark as used
        nonce_info['used'] = True
        
        return True
    
    def get_nonce_context(self, nonce: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve the context associated with a nonce.
        
        Args:
            nonce (str): The nonce to retrieve context for
        
        Returns:
            dict or None: The context associated with the nonce, or None if not found
        """
        return self._nonces.get(nonce, {}).get('context', None)
    
    def clear_expired_nonces(self) -> int:
        """
        Remove expired nonces from the internal storage.
        
        Returns:
            int: Number of nonces removed
        """
        current_time = datetime.now()
        expired_nonces = [
            nonce for nonce, info in self._nonces.items() 
            if current_time > info['expires_at']
        ]
        
        for nonce in expired_nonces:
            del self._nonces[nonce]
        
        return len(expired_nonces)