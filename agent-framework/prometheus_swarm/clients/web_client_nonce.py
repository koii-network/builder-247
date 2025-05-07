import random
import string
from typing import Optional

class WebClientNonceManager:
    """
    A utility class for generating and managing web client nonces.
    
    Nonces (number used once) are random, unique tokens used to prevent 
    replay attacks and ensure request uniqueness.
    """
    
    @staticmethod
    def generate_nonce(length: int = 32) -> str:
        """
        Generate a cryptographically secure random nonce.
        
        Args:
            length (int, optional): Length of the nonce. Defaults to 32.
        
        Returns:
            str: A randomly generated nonce string.
        
        Raises:
            ValueError: If length is less than 16.
        """
        if length < 16:
            raise ValueError("Nonce length must be at least 16 characters")
        
        # Use a combination of uppercase, lowercase, and digits
        characters = string.ascii_letters + string.digits
        
        # Use SystemRandom for cryptographically secure random generation
        secure_random = random.SystemRandom()
        
        nonce = ''.join(secure_random.choice(characters) for _ in range(length))
        return nonce
    
    @staticmethod
    def validate_nonce(nonce: Optional[str], min_length: int = 16, max_length: int = 64) -> bool:
        """
        Validate a nonce's format and characteristics.
        
        Args:
            nonce (Optional[str]): The nonce to validate.
            min_length (int, optional): Minimum acceptable nonce length. Defaults to 16.
            max_length (int, optional): Maximum acceptable nonce length. Defaults to 64.
        
        Returns:
            bool: True if nonce is valid, False otherwise.
        """
        if nonce is None:
            return False
        
        # Check length constraints
        if not (min_length <= len(nonce) <= max_length):
            return False
        
        # Ensure nonce contains only valid characters
        return all(char in string.ascii_letters + string.digits for char in nonce)