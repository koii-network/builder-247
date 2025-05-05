import re
import uuid
from typing import Optional, Union

class TransactionIDManager:
    """
    Utility class for managing and cleaning up transaction IDs.
    
    This class provides methods to:
    - Generate clean transaction IDs
    - Validate transaction IDs
    - Sanitize transaction IDs
    """

    @staticmethod
    def generate_transaction_id() -> str:
        """
        Generate a new, unique transaction ID.
        
        Returns:
            str: A clean, UUID-based transaction ID
        """
        return str(uuid.uuid4())

    @staticmethod
    def sanitize_transaction_id(transaction_id: Optional[Union[str, int]]) -> Optional[str]:
        """
        Sanitize a transaction ID by cleaning and validating it.
        
        Args:
            transaction_id: The transaction ID to sanitize
        
        Returns:
            Optional[str]: A cleaned transaction ID, or None if invalid
        """
        if transaction_id is None:
            return None
        
        # Convert to string and strip whitespace
        cleaned_id = str(transaction_id).strip()
        
        # Remove any non-alphanumeric characters
        cleaned_id = re.sub(r'[^a-zA-Z0-9]', '', cleaned_id)
        
        # Truncate to reasonable length (e.g., 100 characters)
        cleaned_id = cleaned_id[:100]
        
        return cleaned_id if cleaned_id else None

    @staticmethod
    def is_valid_transaction_id(transaction_id: Optional[Union[str, int]]) -> bool:
        """
        Check if a transaction ID is valid.
        
        Args:
            transaction_id: The transaction ID to validate
        
        Returns:
            bool: True if valid, False otherwise
        """
        if transaction_id is None:
            return False
        
        cleaned_id = TransactionIDManager.sanitize_transaction_id(transaction_id)
        
        # Check if cleaned ID is not empty and meets basic criteria
        return (
            cleaned_id is not None and 
            len(cleaned_id) > 0 and 
            len(cleaned_id) <= 50  # More restrictive length
        )