from typing import Optional, Dict, Any
from datetime import datetime, timedelta, timezone
import uuid
import hashlib

class NonceManager:
    """
    Manages nonce generation, storage, and validation.
    
    A nonce is a unique, time-limited token used to prevent replay attacks
    and ensure request uniqueness.
    """
    
    def __init__(self, max_age: int = 3600):
        """
        Initialize the NonceManager.
        
        Args:
            max_age (int): Maximum age of a nonce in seconds before it expires. 
                           Defaults to 1 hour (3600 seconds).
        """
        self._nonce_store: Dict[str, Dict[str, Any]] = {}
        self._max_age = max_age
    
    def generate_nonce(self, context: Optional[str] = None) -> str:
        """
        Generate a unique nonce.
        
        Args:
            context (Optional[str]): Optional context to bind the nonce to.
        
        Returns:
            str: A unique nonce token.
        """
        # Create a unique identifier
        unique_id = str(uuid.uuid4())
        
        # Hash the unique ID for additional security
        nonce = hashlib.sha256(unique_id.encode()).hexdigest()
        
        # Store nonce with timestamp and optional context
        self._nonce_store[nonce] = {
            'timestamp': datetime.now(timezone.utc),
            'context': context,
            'used': False
        }
        
        return nonce
    
    def validate_nonce(self, nonce: str, context: Optional[str] = None) -> bool:
        """
        Validate a nonce.
        
        Args:
            nonce (str): The nonce to validate.
            context (Optional[str]): Optional context to validate against.
        
        Returns:
            bool: True if nonce is valid, False otherwise.
        """
        # Check if nonce exists
        if nonce not in self._nonce_store:
            return False
        
        nonce_data = self._nonce_store[nonce]
        
        # Check if nonce has already been used
        if nonce_data['used']:
            return False
        
        # Check age of nonce
        age = datetime.now(timezone.utc) - nonce_data['timestamp']
        if age > timedelta(seconds=self._max_age):
            del self._nonce_store[nonce]
            return False
        
        # Validate context if provided
        if context is not None and nonce_data['context'] != context:
            return False
        
        # Mark nonce as used
        nonce_data['used'] = True
        
        return True
    
    def clear_expired_nonces(self) -> int:
        """
        Clear expired nonces from the store.
        
        Returns:
            int: Number of expired nonces removed.
        """
        now = datetime.now(timezone.utc)
        expired_nonces = [
            nonce for nonce, data in self._nonce_store.items()
            if (now - data['timestamp']) > timedelta(seconds=self._max_age)
        ]
        
        for nonce in expired_nonces:
            del self._nonce_store[nonce]
        
        return len(expired_nonces)