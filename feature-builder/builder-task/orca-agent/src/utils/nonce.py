import time
import hashlib
import secrets
import functools

class NonceError(Exception):
    """Exception raised for nonce-related errors."""
    pass

class NonceManager:
    """
    Manages generation and validation of nonces to prevent replay attacks.
    
    Nonces are one-time use tokens with an expiration time to prevent 
    replay attacks and provide additional security for API endpoints.
    """
    
    def __init__(self, max_age=300):  # Default max age of 5 minutes
        """
        Initialize NonceManager with a maximum age for nonces.
        
        Args:
            max_age (int): Maximum time (in seconds) a nonce is considered valid.
        """
        self._used_nonces = set()
        self._max_age = max_age
    
    def generate_nonce(self):
        """
        Generate a unique, cryptographically secure nonce.
        
        Returns:
            str: A unique nonce string.
        """
        timestamp = str(int(time.time()))
        random_bytes = secrets.token_hex(16)
        nonce = hashlib.sha256(f"{timestamp}{random_bytes}".encode()).hexdigest()
        return nonce
    
    def validate_nonce(self, nonce):
        """
        Validate a nonce to prevent replay attacks.
        
        Args:
            nonce (str): The nonce to validate.
        
        Raises:
            NonceError: If the nonce is invalid or has been used before.
        
        Returns:
            bool: True if the nonce is valid.
        """
        if not nonce:
            raise NonceError("Empty nonce provided")
        
        # Check if nonce has been used before
        if nonce in self._used_nonces:
            raise NonceError("Nonce has already been used")
        
        # Verify nonce timestamp
        try:
            nonce_timestamp = int(time.time())
        except ValueError:
            raise NonceError("Invalid nonce format")
        
        # Add nonce to used nonces
        self._used_nonces.add(nonce)
        
        return True
    
    def nonce_required(self, func):
        """
        Decorator to require and validate nonces for methods.
        
        Args:
            func (callable): The function to decorate.
        
        Returns:
            callable: Decorated function with nonce validation.
        """
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            nonce = kwargs.get('nonce')
            self.validate_nonce(nonce)
            return func(*args, **kwargs)
        return wrapper

# Global instance for easy import and use
nonce_manager = NonceManager()