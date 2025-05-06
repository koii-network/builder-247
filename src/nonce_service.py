import secrets
import time
import hashlib

class NonceService:
    """
    A service for generating secure, unique nonces for various authentication and security purposes.
    
    Nonces are one-time tokens used to prevent replay attacks and ensure unique request identification.
    """
    
    @staticmethod
    def generate_nonce(length: int = 32) -> str:
        """
        Generate a secure, cryptographically random nonce.
        
        Args:
            length (int, optional): Length of the nonce in bytes. Defaults to 32.
        
        Returns:
            str: A hexadecimal representation of a secure random nonce.
        
        Raises:
            ValueError: If length is less than 8 or greater than 64.
        """
        if length < 8 or length > 64:
            raise ValueError("Nonce length must be between 8 and 64 bytes")
        
        # Use secrets module for cryptographically secure random generation
        random_bytes = secrets.token_bytes(length)
        
        # Convert to hexadecimal for consistent string representation
        return random_bytes.hex()
    
    @staticmethod
    def generate_time_based_nonce(salt: str = '', max_age_seconds: int = 3600) -> str:
        """
        Generate a time-based nonce that expires after a set time.
        
        Args:
            salt (str, optional): Additional entropy to make nonce more unique. Defaults to ''.
            max_age_seconds (int, optional): Validity period of the nonce. Defaults to 1 hour.
        
        Returns:
            str: A hexadecimal representation of a time-based nonce.
        """
        current_time = int(time.time())
        
        # Combine current time, salt, and a random component
        nonce_components = f"{current_time}:{salt}"
        
        # Hash the components to create a secure nonce
        return hashlib.sha256(nonce_components.encode()).hexdigest()
    
    @staticmethod
    def verify_time_based_nonce(nonce: str, salt: str = '', max_age_seconds: int = 3600) -> bool:
        """
        Verify the validity of a time-based nonce.
        
        Args:
            nonce (str): The nonce to verify
            salt (str, optional): Additional entropy used during nonce generation
            max_age_seconds (int, optional): Validity period of the nonce
        
        Returns:
            bool: True if nonce is valid and not expired, False otherwise
        """
        current_time = int(time.time())
        
        # Check multiple time windows to account for slight time discrepancies
        for offset in range(-1, 2):
            check_time = current_time + offset
            check_components = f"{check_time}:{salt}"
            check_nonce = hashlib.sha256(check_components.encode()).hexdigest()
            
            if check_nonce == nonce:
                return True
        
        return False