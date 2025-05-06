import secrets
import time
import hashlib

class NonceService:
    """
    A service for generating secure, unique nonces with configurable parameters.
    
    Nonces are used to prevent replay attacks and ensure request uniqueness.
    """
    
    def __init__(self, 
                 length: int = 32, 
                 include_timestamp: bool = True, 
                 salt: str = ''):
        """
        Initialize the NonceService with configurable nonce generation parameters.
        
        Args:
            length (int, optional): Length of the generated nonce. Defaults to 32.
            include_timestamp (bool, optional): Whether to include a timestamp in nonce generation. 
                                                Defaults to True.
            salt (str, optional): Additional salt for nonce generation. Defaults to empty string.
        """
        self.length = length
        self.include_timestamp = include_timestamp
        self.salt = salt
    
    def generate_nonce(self) -> str:
        """
        Generate a secure, unique nonce.
        
        Returns:
            str: A cryptographically secure nonce
        
        Raises:
            ValueError: If requested nonce length is less than 16
        """
        if self.length < 16:
            raise ValueError("Nonce length must be at least 16 characters")
        
        # Generate random bytes
        random_bytes = secrets.token_bytes(self.length // 2)
        
        if self.include_timestamp:
            # Include current timestamp
            timestamp = str(int(time.time())).encode('utf-8')
            random_bytes += timestamp
        
        # Add optional salt
        if self.salt:
            random_bytes += self.salt.encode('utf-8')
        
        # Hash to create a fixed-length nonce
        nonce = hashlib.sha256(random_bytes).hexdigest()[:self.length]
        
        return nonce
    
    def validate_nonce(self, nonce: str, max_age: int = 3600) -> bool:
        """
        Validate a previously generated nonce.
        
        Args:
            nonce (str): The nonce to validate
            max_age (int, optional): Maximum age of nonce in seconds. Defaults to 1 hour.
        
        Returns:
            bool: Whether the nonce is valid
        """
        if not nonce or len(nonce) != self.length:
            return False
        
        if self.include_timestamp:
            try:
                # Extract timestamp from nonce generation
                timestamp_str = nonce[-10:]  # Assuming timestamp is 10 digits
                nonce_timestamp = int(timestamp_str)
                current_time = int(time.time())
                
                # Check timestamp age
                if current_time - nonce_timestamp > max_age:
                    return False
            except (ValueError, TypeError):
                return False
        
        return True