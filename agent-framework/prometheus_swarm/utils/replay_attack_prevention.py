import time
import hashlib
from typing import Dict, Optional, Any

class ReplayAttackPrevention:
    """
    A utility class to prevent replay attacks by tracking and validating request uniqueness.
    
    This class provides mechanisms to:
    1. Generate unique tokens for requests
    2. Validate tokens to prevent replay attacks
    3. Configure replay attack prevention settings
    """
    
    def __init__(
        self, 
        max_token_age: int = 300,  # Default: 5 minutes
        max_tokens: int = 1000,    # Maximum number of tokens to store
        enabled: bool = True
    ):
        """
        Initialize the Replay Attack Prevention mechanism.
        
        Args:
            max_token_age (int): Maximum age of a valid token in seconds. Defaults to 300 (5 minutes).
            max_tokens (int): Maximum number of tokens to store to prevent memory exhaustion. Defaults to 1000.
            enabled (bool): Whether replay attack prevention is enabled. Defaults to True.
        """
        self._tokens: Dict[str, float] = {}
        self._max_token_age = max_token_age
        self._max_tokens = max_tokens
        self._enabled = enabled
    
    def _cleanup_expired_tokens(self):
        """Remove tokens that have exceeded the maximum age."""
        current_time = time.time()
        expired_tokens = [
            token for token, timestamp in self._tokens.items() 
            if current_time - timestamp > self._max_token_age
        ]
        
        for token in expired_tokens:
            del self._tokens[token]
    
    def _enforce_max_tokens(self):
        """Enforce the maximum number of tokens."""
        if len(self._tokens) > self._max_tokens:
            # Remove the oldest tokens
            oldest_tokens = sorted(
                self._tokens.items(), 
                key=lambda x: x[1]
            )[:len(self._tokens) - self._max_tokens]
            
            for token, _ in oldest_tokens:
                del self._tokens[token]
    
    def generate_token(self, payload: Optional[Any] = None) -> str:
        """
        Generate a unique, time-bound token to prevent replay attacks.
        
        Args:
            payload (Optional[Any]): Optional payload to include in token generation.
        
        Returns:
            str: A unique token that can be used to validate request uniqueness.
        """
        if not self._enabled:
            return ""
        
        current_time = time.time()
        
        # Cleanup expired tokens
        self._cleanup_expired_tokens()
        
        # Include current timestamp and optional payload in token generation
        token_data = f"{current_time}:{payload}"
        token = hashlib.sha256(token_data.encode()).hexdigest()
        
        # Store the token
        self._tokens[token] = current_time
        
        # Enforce max tokens
        self._enforce_max_tokens()
        
        return token
    
    def validate_token(self, token: str) -> bool:
        """
        Validate a token to prevent replay attacks.
        
        Args:
            token (str): The token to validate.
        
        Returns:
            bool: True if the token is valid and has not been used before, False otherwise.
        """
        if not self._enabled or not token:
            return True
        
        # Cleanup expired tokens
        self._cleanup_expired_tokens()
        
        # Check if token exists
        if token in self._tokens:
            del self._tokens[token]  # Token can only be used once
            return True
        
        return False
    
    def configure(
        self, 
        max_token_age: Optional[int] = None, 
        max_tokens: Optional[int] = None, 
        enabled: Optional[bool] = None
    ):
        """
        Configure replay attack prevention settings.
        
        Args:
            max_token_age (Optional[int]): New maximum age for tokens.
            max_tokens (Optional[int]): New maximum number of tokens to store.
            enabled (Optional[bool]): Enable or disable replay attack prevention.
        """
        if max_token_age is not None:
            self._max_token_age = max_token_age
        
        if max_tokens is not None:
            self._max_tokens = max_tokens
        
        if enabled is not None:
            self._enabled = enabled
        
        # Cleanup and enforce limits
        self._cleanup_expired_tokens()
        self._enforce_max_tokens()
    
    def get_config(self) -> Dict[str, Any]:
        """
        Retrieve the current replay attack prevention configuration.
        
        Returns:
            Dict[str, Any]: Configuration settings.
        """
        return {
            "max_token_age": self._max_token_age,
            "max_tokens": self._max_tokens,
            "enabled": self._enabled
        }

# Global singleton instance for easy configuration
replay_attack_prevention = ReplayAttackPrevention()