import re
import uuid

class TransactionIDValidator:
    """
    A utility class for validating transaction IDs.
    
    Supports multiple validation strategies:
    1. UUID validation (version 4)
    2. Custom format validation
    3. Length-based validation
    """
    
    @staticmethod
    def validate_uuid(transaction_id: str) -> bool:
        """
        Validate if the transaction ID is a valid UUID (version 4).
        
        Args:
            transaction_id (str): The transaction ID to validate
        
        Returns:
            bool: True if valid UUID, False otherwise
        """
        try:
            # Attempt to validate as UUID v4
            uuid_obj = uuid.UUID(transaction_id, version=4)
            return str(uuid_obj) == transaction_id
        except (ValueError, AttributeError):
            return False
    
    @staticmethod
    def validate_custom_format(transaction_id: str, 
                                pattern: str = r'^[A-Z]{2}\d{6}[A-Z]{2}$') -> bool:
        """
        Validate transaction ID against a custom regex pattern.
        
        Default pattern: 2 uppercase letters, 6 digits, 2 uppercase letters
        
        Args:
            transaction_id (str): The transaction ID to validate
            pattern (str, optional): Custom regex pattern. Defaults to strict format.
        
        Returns:
            bool: True if matches pattern, False otherwise
        """
        return bool(re.match(pattern, transaction_id))
    
    @staticmethod
    def validate_length(transaction_id: str, 
                        min_length: int = 10, 
                        max_length: int = 50) -> bool:
        """
        Validate transaction ID length.
        
        Args:
            transaction_id (str): The transaction ID to validate
            min_length (int, optional): Minimum allowed length. Defaults to 10.
            max_length (int, optional): Maximum allowed length. Defaults to 50.
        
        Returns:
            bool: True if length is within range, False otherwise
        """
        return min_length <= len(transaction_id) <= max_length
    
    @classmethod
    def validate(cls, 
                 transaction_id: str, 
                 uuid_validation: bool = True,
                 custom_pattern: str = None,
                 min_length: int = 10,
                 max_length: int = 50) -> bool:
        """
        Comprehensive transaction ID validation.
        
        Args:
            transaction_id (str): The transaction ID to validate
            uuid_validation (bool, optional): Enable UUID validation. Defaults to True.
            custom_pattern (str, optional): Custom regex pattern for validation
            min_length (int, optional): Minimum allowed length
            max_length (int, optional): Maximum allowed length
        
        Returns:
            bool: True if all enabled validations pass, False otherwise
        
        Raises:
            TypeError: If transaction_id is not a string
        """
        # Type checking
        if not isinstance(transaction_id, str):
            raise TypeError("Transaction ID must be a string")
        
        # Validate length first
        if not cls.validate_length(transaction_id, min_length, max_length):
            return False
        
        # UUID validation
        if uuid_validation and not cls.validate_uuid(transaction_id):
            return False
        
        # Custom pattern validation
        if custom_pattern and not cls.validate_custom_format(transaction_id, custom_pattern):
            return False
        
        return True