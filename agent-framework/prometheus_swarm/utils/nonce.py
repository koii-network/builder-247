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
                 salt: str = '',
                 max_age: int = 3600):
        """
        Initialize the NonceService with configurable nonce generation parameters.
        
        Args:
            length (int, optional): Length of the generated nonce. Defaults to 32.
            include_timestamp (bool, optional): Whether to include a timestamp in nonce generation. 
                                                Defaults to True.
            salt (str, optional): Additional salt for nonce generation. Defaults to empty string.
            max_age (int, optional): Maximum age of a nonce in seconds. Defaults to 1 hour.
        """
        if length < 16:
            raise ValueError("Nonce length must be at least 16 characters")
        
        self.length = length
        self.include_timestamp = include_timestamp
        self.salt = salt
        self.max_age = max_age
        self._used_nonces = set()
    
    def generate_nonce(self) -> str:
        """
        Generate a secure, unique nonce.
        
        Returns:
            str: A cryptographically secure nonce
        """
        # Generate random bytes
        random_bytes = secrets.token_bytes(self.length // 2)
        
        # Include current timestamp if enabled
        timestamp = str(int(time.time())).encode('utf-8') if self.include_timestamp else b''
        
        # Add optional salt
        salt_bytes = self.salt.encode('utf-8') if self.salt else b''
        
        # Combine all inputs
        combined_bytes = random_bytes + timestamp + salt_bytes
        
        # Hash to create a fixed-length nonce
        nonce = hashlib.sha256(combined_bytes).hexdigest()[:self.length]
        
        # Mark nonce as used
        self._used_nonces.add(nonce)
        
        return nonce
    
    def validate_nonce(self, nonce: str) -> bool:
        """
        Validate a previously generated nonce.
        
        Args:
            nonce (str): The nonce to validate
        
        Returns:
            bool: Whether the nonce is valid
        """
        # Check basic requirements
        if not nonce or len(nonce) != self.length or nonce not in self._used_nonces:
            return False
        
        # If timestamp is included, validate age
        if self.include_timestamp:
            try:
                # Extract timestamp from the last 10 characters
                timestamp_str = nonce[-10:]
                nonce_timestamp = int(timestamp_str, 16)  # Convert hex timestamp
                current_time = int(time.time())
                
                # Check timestamp age
                if current_time - nonce_timestamp > self.max_age:
                    self._used_nonces.remove(nonce)
                    return False
            except (ValueError, TypeError):
                return False
        
        return True