import re
from typing import Union, Optional

class TransactionIDCleanup:
    """
    A utility class for cleaning and validating transaction IDs.
    
    This class provides methods to sanitize, normalize, and validate 
    transaction identifiers across different formats.
    """
    
    @staticmethod
    def clean_transaction_id(transaction_id: Union[str, int, None]) -> Optional[str]:
        """
        Clean and normalize a transaction ID.
        
        Args:
            transaction_id (Union[str, int, None]): The transaction ID to clean.
        
        Returns:
            Optional[str]: A cleaned and normalized transaction ID, or None if invalid.
        
        Raises:
            TypeError: If input is not a string, integer, or None.
        """
        if transaction_id is None:
            return None
        
        # Convert to string if integer
        if isinstance(transaction_id, int):
            transaction_id = str(transaction_id)
        
        # Validate input type
        if not isinstance(transaction_id, str):
            raise TypeError("Transaction ID must be a string, integer, or None")
        
        # Remove whitespace
        cleaned_id = transaction_id.strip()
        
        # Convert to lowercase
        cleaned_id = cleaned_id.lower()
        
        # Remove any non-alphanumeric characters except hyphens and underscores
        cleaned_id = re.sub(r'[^a-z0-9\-_]', '', cleaned_id)
        
        return cleaned_id if cleaned_id else None
    
    @staticmethod
    def validate_transaction_id(transaction_id: Optional[str], 
                                 min_length: int = 5, 
                                 max_length: int = 50) -> bool:
        """
        Validate a transaction ID based on configurable criteria.
        
        Args:
            transaction_id (Optional[str]): The transaction ID to validate.
            min_length (int, optional): Minimum allowed length. Defaults to 5.
            max_length (int, optional): Maximum allowed length. Defaults to 50.
        
        Returns:
            bool: True if the transaction ID is valid, False otherwise.
        """
        if transaction_id is None:
            return False
        
        # Check length constraints
        if len(transaction_id) < min_length or len(transaction_id) > max_length:
            return False
        
        # Ensure only valid characters are present
        return bool(re.match(r'^[a-z0-9\-_]+$', transaction_id))