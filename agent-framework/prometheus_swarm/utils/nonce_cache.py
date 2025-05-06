import redis
import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class NonceCache:
    """
    A utility class for managing nonce caching using Redis.
    
    Provides methods to store, check, and manage nonces to prevent replay attacks
    and ensure request uniqueness.
    """
    
    def __init__(self, 
                 redis_host: str = None, 
                 redis_port: int = None, 
                 redis_db: int = None,
                 nonce_expiry: int = 3600):
        """
        Initialize the Redis connection for nonce caching.
        
        Args:
            redis_host (str, optional): Redis server host. Defaults to env var or 'localhost'.
            redis_port (int, optional): Redis server port. Defaults to env var or 6379.
            redis_db (int, optional): Redis database number. Defaults to env var or 0.
            nonce_expiry (int, optional): Nonce expiration time in seconds. Defaults to 1 hour.
        """
        # Use environment variables or default values
        self.redis_host = redis_host or os.getenv('REDIS_HOST', 'localhost')
        self.redis_port = redis_port or int(os.getenv('REDIS_PORT', 6379))
        self.redis_db = redis_db or int(os.getenv('REDIS_DB', 0))
        
        # Nonce expiration time
        self.nonce_expiry = nonce_expiry
        
        # Create Redis client
        self.redis_client = redis.Redis(
            host=self.redis_host, 
            port=self.redis_port, 
            db=self.redis_db
        )
    
    def store_nonce(self, nonce: str) -> bool:
        """
        Store a nonce in Redis with an expiration time.
        
        Args:
            nonce (str): The unique nonce to store.
        
        Returns:
            bool: True if nonce was successfully stored, False if already exists.
        """
        if not nonce:
            raise ValueError("Nonce cannot be empty")
        
        # Use Redis set with NX (only set if not exists) and EX (expiry)
        return bool(self.redis_client.set(
            f"nonce:{nonce}", 
            "1", 
            ex=self.nonce_expiry, 
            nx=True
        ))
    
    def is_nonce_used(self, nonce: str) -> bool:
        """
        Check if a nonce has already been used.
        
        Args:
            nonce (str): The nonce to check.
        
        Returns:
            bool: True if nonce exists (has been used), False otherwise.
        """
        if not nonce:
            raise ValueError("Nonce cannot be empty")
        
        return bool(self.redis_client.exists(f"nonce:{nonce}"))
    
    def invalidate_nonce(self, nonce: str) -> bool:
        """
        Manually invalidate a nonce before its natural expiration.
        
        Args:
            nonce (str): The nonce to invalidate.
        
        Returns:
            bool: True if nonce was successfully invalidated, False if it didn't exist.
        """
        if not nonce:
            raise ValueError("Nonce cannot be empty")
        
        return bool(self.redis_client.delete(f"nonce:{nonce}"))
    
    def clear_all_nonces(self) -> int:
        """
        Clear all stored nonces from Redis.
        
        Returns:
            int: Number of nonces deleted.
        """
        # Find and delete all keys matching the nonce pattern
        nonce_keys = self.redis_client.keys("nonce:*")
        if nonce_keys:
            return self.redis_client.delete(*nonce_keys)
        return 0