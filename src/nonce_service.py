import secrets
import time
import hashlib

class NonceService:
    """
    A service for generating secure, unique nonces with configurable parameters.
    
    Nonces are used to prevent replay attacks and ensure request uniqueness.
    """
    
    @staticmethod
    def generate_nonce(length=32, include_timestamp=True):
        """
        Generate a cryptographically secure nonce.
        
        Args:
            length (int, optional): Length of the nonce. Defaults to 32.
            include_timestamp (bool, optional): Whether to include a timestamp. Defaults to True.
        
        Returns:
            str: A secure nonce string
        
        Raises:
            ValueError: If length is less than 8 or greater than 128
        """
        if length < 8 or length > 128:
            raise ValueError("Nonce length must be between 8 and 128 characters")
        
        # Generate cryptographically secure random bytes
        # Use ceil division to ensure enough bytes
        random_bytes = secrets.token_bytes((length + 1) // 2)
        hex_random = random_bytes.hex()
        
        # Optionally include timestamp for additional uniqueness
        if include_timestamp:
            timestamp = str(int(time.time()))
            # Combine random hex with timestamp and hash
            combined = hex_random + timestamp
            nonce = hashlib.sha256(combined.encode()).hexdigest()
        else:
            nonce = hex_random
        
        # Ensure exact length by truncating or padding
        return nonce[:length].ljust(length, '0')
    
    @staticmethod
    def validate_nonce(nonce, max_age=3600):
        """
        Validate a nonce's format and age.
        
        Args:
            nonce (str): The nonce to validate
            max_age (int, optional): Maximum age of nonce in seconds. Defaults to 1 hour.
        
        Returns:
            bool: Whether the nonce is valid
        
        Raises:
            TypeError: If nonce is not a string
        """
        if not isinstance(nonce, str):
            raise TypeError("Nonce must be a string")
        
        # Check basic format (hex characters)
        if not all(c in '0123456789abcdef' for c in nonce.lower()):
            return False
        
        # Optional timestamp validation (if included)
        try:
            # Try to extract timestamp (assuming last part of nonce is timestamp)
            timestamp_str = ''.join(filter(str.isdigit, nonce))
            if timestamp_str:
                timestamp = int(timestamp_str)
                current_time = int(time.time())
                
                # Check if nonce is within max_age
                if current_time - timestamp > max_age:
                    return False
        except (ValueError, TypeError):
            # If timestamp extraction fails, consider it valid
            pass
        
        return True