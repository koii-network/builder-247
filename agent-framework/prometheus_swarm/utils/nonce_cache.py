import os
import hashlib
import time
import redis
from typing import Optional, Union

class NonceCache:
    """
    A Redis-based nonce caching mechanism to prevent replay attacks and ensure unique request processing.
    
    Features:
    - Store nonces in Redis with an expiration time
    - Validate whether a nonce has been used before
    - Configurable nonce expiration
    """
    
    def __init__(
        self, 
        redis_url: Optional[str] = None, 
        nonce_expiration: int = 3600  # Default 1 hour
    ):
        """
        Initialize the NonceCache with Redis connection.
        
        :param redis_url: Redis connection URL (defaults to localhost if not provided)
        :param nonce_expiration: Time in seconds after which a nonce expires
        """
        # Use environment variable or default to local Redis
        self.redis_url = redis_url or os.getenv('REDIS_URL', 'redis://localhost:6379/0')
        self.nonce_expiration = nonce_expiration
        
        try:
            self.redis_client = redis.from_url(self.redis_url)
            # Verify Redis connection
            self.redis_client.ping()
        except Exception as e:
            raise ConnectionError(f"Unable to connect to Redis: {e}")
    
    def generate_nonce(self, data: Union[str, bytes, int, float]) -> str:
        """
        Generate a unique nonce based on input data and current timestamp.
        
        :param data: Input data to generate nonce from
        :return: A unique nonce string
        """
        # Convert data to string/bytes if not already
        if not isinstance(data, (str, bytes)):
            data = str(data)
        
        # Combine data with current timestamp
        unique_input = f"{data}:{time.time()}"
        
        # Create a secure hash
        return hashlib.sha256(unique_input.encode()).hexdigest()
    
    def store_nonce(self, nonce: str) -> bool:
        """
        Store a nonce in Redis with an expiration time.
        
        :param nonce: Nonce to store
        :return: True if nonce was successfully stored, False otherwise
        """
        try:
            # Use Redis SET with NX (only set if not exists) and EX (expiration)
            result = self.redis_client.set(
                f"nonce:{nonce}", 
                "1", 
                nx=True,  # Only set if not exists
                ex=self.nonce_expiration  # Expire after set time
            )
            return bool(result)
        except Exception as e:
            raise RuntimeError(f"Error storing nonce: {e}")
    
    def is_nonce_valid(self, nonce: str) -> bool:
        """
        Check if a nonce is valid (not previously used).
        
        :param nonce: Nonce to validate
        :return: True if nonce is valid and unique, False otherwise
        """
        try:
            # Attempt to store nonce atomically
            return self.store_nonce(nonce)
        except Exception as e:
            raise RuntimeError(f"Error validating nonce: {e}")