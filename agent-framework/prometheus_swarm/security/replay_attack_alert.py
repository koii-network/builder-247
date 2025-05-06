"""
Replay Attack Alert Mechanism

This module provides functionality to detect and prevent replay attacks
by tracking and validating unique request identifiers.
"""

import time
from typing import Dict, Any, Optional
from functools import wraps

class ReplayAttackPreventor:
    """
    A class to prevent replay attacks by tracking and validating request signatures.
    
    Attributes:
        _request_cache (Dict[str, float]): Stores request signatures and their timestamps
        _cache_expiry_seconds (int): Duration after which a request signature expires
    """
    
    def __init__(self, cache_expiry_seconds: int = 300):
        """
        Initialize the Replay Attack Preventor.
        
        Args:
            cache_expiry_seconds (int, optional): Time in seconds after which a request signature expires. 
                                                  Defaults to 300 seconds (5 minutes).
        """
        self._request_cache: Dict[str, float] = {}
        self._cache_expiry_seconds = cache_expiry_seconds
    
    def _clean_expired_entries(self) -> None:
        """
        Remove expired request signatures from the cache.
        """
        current_time = time.time()
        expired_keys = [
            key for key, timestamp in self._request_cache.items() 
            if current_time - timestamp > self._cache_expiry_seconds
        ]
        
        for key in expired_keys:
            del self._request_cache[key]
    
    def is_replay_attempt(self, request_signature: str) -> bool:
        """
        Check if a request is a potential replay attack.
        
        Args:
            request_signature (str): A unique identifier for the request.
        
        Returns:
            bool: True if the request is a replay attempt, False otherwise.
        """
        self._clean_expired_entries()
        
        if request_signature in self._request_cache:
            return True
        
        self._request_cache[request_signature] = time.time()
        return False

def prevent_replay_attack(request_signature_func=None, 
                           expiry_seconds: int = 300, 
                           raise_on_replay: bool = False):
    """
    A decorator to prevent replay attacks on functions.
    
    Args:
        request_signature_func (callable, optional): A function to generate request signature. 
                                                    Defaults to None.
        expiry_seconds (int, optional): Time in seconds for request signature expiry. 
                                        Defaults to 300 seconds.
        raise_on_replay (bool, optional): Whether to raise an exception on replay attempt. 
                                          Defaults to False.
    
    Returns:
        callable: Decorated function with replay attack prevention
    """
    preventor = ReplayAttackPreventor(cache_expiry_seconds=expiry_seconds)
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Default signature generation if no function provided
            if request_signature_func is None:
                request_signature = str(hash(repr(args) + repr(kwargs)))
            else:
                request_signature = request_signature_func(*args, **kwargs)
            
            if preventor.is_replay_attempt(request_signature):
                if raise_on_replay:
                    raise ValueError(f"Potential replay attack detected for signature: {request_signature}")
                return None
            
            return func(*args, **kwargs)
        return wrapper
    return decorator