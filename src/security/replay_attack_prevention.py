import time
import hashlib
from typing import Dict, Any, Optional

class ReplayAttackPrevention:
    """
    A class to prevent replay attacks by tracking and validating request tokens.

    Replay attacks occur when an attacker intercepts a valid data transmission 
    and maliciously retransmits it to achieve an unauthorized effect.

    This implementation uses a combination of:
    1. Timestamp-based expiration
    2. Unique token tracking
    3. Configurable time window for token validity
    """

    def __init__(self, token_expiry_seconds: int = 300):
        """
        Initialize the replay attack prevention mechanism.

        :param token_expiry_seconds: Duration in seconds after which a token becomes invalid
        """
        self._used_tokens: Dict[str, float] = {}
        self._token_expiry = token_expiry_seconds

    def generate_token(self, data: Any) -> str:
        """
        Generate a unique token for a given piece of data.

        :param data: Data to generate a token for
        :return: A unique token representing the data
        """
        current_time = time.time()
        # Combine data with current timestamp to create a unique token
        token_input = f"{str(data)}:{current_time}"
        return hashlib.sha256(token_input.encode()).hexdigest()

    def validate_token(self, token: str) -> bool:
        """
        Validate a token against replay attack conditions.

        :param token: Token to validate
        :return: Boolean indicating if the token is valid
        """
        current_time = time.time()

        # Check if token has been used before
        if token in self._used_tokens:
            return False

        # Clean up expired tokens
        self._cleanup_expired_tokens(current_time)

        # Mark token as used and track its timestamp
        self._used_tokens[token] = current_time
        return True

    def _cleanup_expired_tokens(self, current_time: float) -> None:
        """
        Remove tokens that have expired.

        :param current_time: Current timestamp
        """
        self._used_tokens = {
            token: timestamp 
            for token, timestamp in self._used_tokens.items() 
            if current_time - timestamp < self._token_expiry
        }

    def reset(self) -> None:
        """
        Reset the used tokens cache.
        """
        self._used_tokens.clear()