import redis
import time
import hashlib
import os

class NonceCache:
    """
    A Redis-based nonce caching mechanism to prevent replay attacks.
    
    This class provides methods to:
    - Store unique nonces with expiration
    - Check if a nonce has been used before
    """
    
    def __init__(self, 
                 redis_host=None, 
                 redis_port=6379, 
                 redis_db=0, 
                 nonce_expiration=3600):
        """
        Initialize the NonceCache with Redis connection parameters.
        
        :param redis_host: Redis server host (default: localhost)
        :param redis_port: Redis server port (default: 6379)
        :param redis_db: Redis database number (default: 0)
        :param nonce_expiration: Nonce expiration time in seconds (default: 1 hour)
        """
        self.redis_host = redis_host or os.getenv('REDIS_HOST', 'localhost')
        self.redis_port = redis_port
        self.redis_db = redis_db
        self.nonce_expiration = nonce_expiration
        
        self.redis_client = redis.Redis(
            host=self.redis_host, 
            port=self.redis_port, 
            db=self.redis_db
        )
    
    def generate_nonce(self, context=None):
        """
        Generate a unique nonce with optional context.
        
        :param context: Optional context to add to nonce generation
        :return: A unique nonce string
        """
        timestamp = str(int(time.time()))
        context_str = str(context) if context is not None else ''
        
        # Create a hash that combines timestamp, context, and random data
        nonce = hashlib.sha256(
            f"{timestamp}{context_str}{os.urandom(16)}".encode()
        ).hexdigest()
        
        return nonce
    
    def store_nonce(self, nonce, context=None):
        """
        Store a nonce in Redis with an expiration time.
        
        :param nonce: Nonce to store
        :param context: Optional context associated with the nonce
        :return: True if nonce is successfully stored, False otherwise
        """
        try:
            key = f"nonce:{context or 'default'}:{nonce}"
            result = self.redis_client.setex(key, self.nonce_expiration, 1)
            return result
        except redis.exceptions.RedisError:
            return False
    
    def is_nonce_used(self, nonce, context=None):
        """
        Check if a nonce has been used before.
        
        :param nonce: Nonce to check
        :param context: Optional context associated with the nonce
        :return: True if nonce is already used, False otherwise
        """
        try:
            key = f"nonce:{context or 'default'}:{nonce}"
            return bool(self.redis_client.exists(key))
        except redis.exceptions.RedisError:
            return True  # Treat Redis errors as the nonce being used
    
    def invalidate_nonce(self, nonce, context=None):
        """
        Manually invalidate a nonce.
        
        :param nonce: Nonce to invalidate
        :param context: Optional context associated with the nonce
        :return: Number of keys deleted
        """
        try:
            key = f"nonce:{context or 'default'}:{nonce}"
            return self.redis_client.delete(key)
        except redis.exceptions.RedisError:
            return 0