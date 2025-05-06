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
        self._used_nonces = {}
    
    def generate_nonce(self, current_time: float = None) -> str:
        """
        Generate a secure, unique nonce.
        
        Args:
            current_time (float, optional): Specific time to use for nonce. 
                                            Defaults to current system time.
        
        Returns:
            str: A cryptographically secure nonce
        """
        current_time = current_time or time.time()
        
        # Generate random bytes
        random_bytes = secrets.token_bytes(self.length // 2)
        
        # Include current timestamp if enabled
        timestamp_bytes = str(int(current_time)).encode('utf-8') if self.include_timestamp else b''
        
        # Add optional salt
        salt_bytes = self.salt.encode('utf-8') if self.salt else b''
        
        # Combine all inputs
        combined_bytes = random_bytes + timestamp_bytes + salt_bytes
        
        # Hash to create a fixed-length nonce
        nonce = hashlib.sha256(combined_bytes).hexdigest()[:self.length]
        
        # Store nonce with generation time
        self._used_nonces[nonce] = current_time
        
        return nonce
    
    def validate_nonce(self, nonce: str, current_time: float = None) -> bool:
        """
        Validate a previously generated nonce.
        
        Args:
            nonce (str): The nonce to validate
            current_time (float, optional): Specific time to use for validation. 
                                            Defaults to current system time.
        
        Returns:
            bool: Whether the nonce is valid
        """
        current_time = current_time or time.time()
        
        # Check basic requirements
        if not nonce or len(nonce) != self.length or nonce not in self._used_nonces:
            return False
        
        # If timestamp is included, validate age
        if self.include_timestamp:
            nonce_timestamp = self._used_nonces[nonce]
            
            # Check timestamp age
            if current_time - nonce_timestamp > self.max_age:
                del self._used_nonces[nonce]
                return False
        
        return True