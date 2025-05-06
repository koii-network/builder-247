import redis
import time
import hashlib
import uuid
from typing import Optional, Union

class NonceCache:
    """
    A Redis-based Nonce Caching Mechanism for preventing replay attacks and ensuring request uniqueness.
    
    This class provides methods to:
    - Generate unique nonces
    - Validate nonces
    - Manage nonce expiration
    """
    
    def __init__(self, 
                 redis_host: str = 'localhost', 
                 redis_port: int = 6379, 
                 redis_db: int = 0, 
                 nonce_expiry: int = 3600,
                 mock_mode: bool = False):
        """
        Initialize the NonceCache with Redis connection and nonce expiry settings.
        
        Args:
            redis_host (str): Redis server hostname. Defaults to 'localhost'.
            redis_port (int): Redis server port. Defaults to 6379.
            redis_db (int): Redis database number. Defaults to 0.
            nonce_expiry (int): Nonce expiration time in seconds. Defaults to 1 hour.
            mock_mode (bool): If True, use an in-memory dictionary instead of Redis. Defaults to False.
        """
        self.nonce_expiry = nonce_expiry
        self.mock_mode = mock_mode
        
        if mock_mode:
            self.redis_client = {}
        else:
            try:
                self.redis_client = redis.Redis(host=redis_host, port=redis_port, db=redis_db)
            except Exception as e:
                print(f"Redis connection error: {e}")
                # Fallback to mock mode
                self.mock_mode = True
                self.redis_client = {}
    
    def generate_nonce(self, context: Optional[str] = None) -> str:
        """
        Generate a unique, cryptographically secure nonce.
        
        Args:
            context (Optional[str]): Optional context to make nonce generation more specific.
        
        Returns:
            str: A unique nonce string.
        """
        # Combine current timestamp, a UUID, and optional context
        unique_str = f"{time.time()}:{uuid.uuid4()}:{context or ''}"
        
        # Create a secure hash to generate the nonce
        nonce = hashlib.sha256(unique_str.encode()).hexdigest()
        
        return nonce
    
    def store_nonce(self, nonce: str, context: Optional[str] = None) -> bool:
        """
        Store a nonce in Redis with an expiration time.
        
        Args:
            nonce (str): The nonce to store.
            context (Optional[str]): Optional context for more specific nonce tracking.
        
        Returns:
            bool: True if nonce was successfully stored, False otherwise.
        """
        # Create a Redis key with optional context
        key = f"nonce:{context or ''}:{nonce}"
        
        try:
            if self.mock_mode:
                # In mock mode, store in dictionary with timestamp
                self.redis_client[key] = {
                    'value': 1,
                    'timestamp': time.time()
                }
                return True
            
            # Store nonce with expiration
            return bool(self.redis_client.setex(key, self.nonce_expiry, 1))
        except Exception as e:
            # Log or handle Redis connection/storage errors
            print(f"Error storing nonce: {e}")
            return False
    
    def validate_nonce(self, nonce: str, context: Optional[str] = None) -> bool:
        """
        Validate if a nonce is unique and not yet used.
        
        Args:
            nonce (str): The nonce to validate.
            context (Optional[str]): Optional context for more specific nonce validation.
        
        Returns:
            bool: True if nonce is valid and unique, False otherwise.
        """
        # Create a Redis key with optional context
        key = f"nonce:{context or ''}:{nonce}"
        
        try:
            if self.mock_mode:
                # In mock mode, simulate Redis behavior
                if key in self.redis_client:
                    # Check if the entry has expired
                    current_time = time.time()
                    entry_time = self.redis_client[key]['timestamp']
                    
                    if current_time - entry_time >= self.nonce_expiry:
                        del self.redis_client[key]
                    else:
                        return False
                
                # Store nonce for tracking
                self.store_nonce(nonce, context)
                return True
            
            # Check if nonce exists in Redis
            if self.redis_client.exists(key):
                return False
            
            # If nonce doesn't exist, store it and return True
            return self.store_nonce(nonce, context)
        except Exception as e:
            # Log or handle Redis connection/validation errors
            print(f"Error validating nonce: {e}")
            return False
    
    def clear_nonce(self, nonce: str, context: Optional[str] = None) -> bool:
        """
        Manually clear a specific nonce.
        
        Args:
            nonce (str): The nonce to clear.
            context (Optional[str]): Optional context for more specific nonce clearing.
        
        Returns:
            bool: True if nonce was successfully cleared, False otherwise.
        """
        key = f"nonce:{context or ''}:{nonce}"
        
        try:
            if self.mock_mode:
                # In mock mode, remove from dictionary
                if key in self.redis_client:
                    del self.redis_client[key]
                return True
            
            return bool(self.redis_client.delete(key))
        except Exception as e:
            print(f"Error clearing nonce: {e}")
            return False