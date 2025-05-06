import redis
import os
import time
from datetime import timedelta
from dotenv import load_dotenv
from typing import Dict

load_dotenv()

class NonceCache:
    """
    A utility class for managing nonce caching using Redis or fallback in-memory cache.
    
    Provides methods to store, check, and manage nonces to prevent replay attacks
    and ensure request uniqueness.
    """
    
    def __init__(self, 
                 redis_host: str = None, 
                 redis_port: int = None, 
                 redis_db: int = None,
                 nonce_expiry: int = 3600):
        """
        Initialize the NonceCache.
        
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
        
        # In-memory fallback cache
        self._memory_cache: Dict[str, float] = {}
        
        # Try to create Redis client, fallback to memory cache if connection fails
        try:
            self.redis_client = redis.Redis(
                host=self.redis_host, 
                port=self.redis_port, 
                db=self.redis_db
            )
            # Test connection
            self.redis_client.ping()
            self._use_redis = True
        except (redis.exceptions.ConnectionError, ConnectionRefusedError):
            # Fallback to in-memory cache if Redis is not available
            self._use_redis = False
            self.redis_client = None
    
    def store_nonce(self, nonce: str) -> bool:
        """
        Store a nonce with an expiration time.
        
        Args:
            nonce (str): The unique nonce to store.
        
        Returns:
            bool: True if nonce was successfully stored, False if already exists.
        """
        if not nonce:
            raise ValueError("Nonce cannot be empty")
        
        # Clean up expired in-memory entries
        current_time = time.time()
        self._memory_cache = {
            k: v for k, v in self._memory_cache.items() 
            if v > current_time
        }
        
        if self._use_redis:
            # Use Redis set with NX (only set if not exists) and EX (expiry)
            return bool(self.redis_client.set(
                f"nonce:{nonce}", 
                "1", 
                ex=self.nonce_expiry, 
                nx=True
            ))
        else:
            # In-memory implementation
            nonce_key = f"nonce:{nonce}"
            if nonce_key in self._memory_cache:
                return False
            
            # Store with expiration
            self._memory_cache[nonce_key] = current_time + self.nonce_expiry
            return True
    
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
        
        # Clean up expired in-memory entries
        current_time = time.time()
        self._memory_cache = {
            k: v for k, v in self._memory_cache.items() 
            if v > current_time
        }
        
        if self._use_redis:
            return bool(self.redis_client.exists(f"nonce:{nonce}"))
        else:
            # In-memory implementation
            return f"nonce:{nonce}" in self._memory_cache
    
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
        
        if self._use_redis:
            return bool(self.redis_client.delete(f"nonce:{nonce}"))
        else:
            # In-memory implementation
            nonce_key = f"nonce:{nonce}"
            if nonce_key in self._memory_cache:
                del self._memory_cache[nonce_key]
                return True
            return False
    
    def clear_all_nonces(self) -> int:
        """
        Clear all stored nonces.
        
        Returns:
            int: Number of nonces deleted.
        """
        if self._use_redis:
            # Find and delete all keys matching the nonce pattern
            nonce_keys = self.redis_client.keys("nonce:*")
            if nonce_keys:
                return self.redis_client.delete(*nonce_keys)
            return 0
        else:
            # In-memory implementation
            count = len(self._memory_cache)
            self._memory_cache.clear()
            return count