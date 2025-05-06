import re
import uuid

def validate_transaction_id(transaction_id: str) -> bool:
    """
    Validate a transaction ID based on specific criteria.
    
    Args:
        transaction_id (str): The transaction ID to validate.
    
    Returns:
        bool: True if the transaction ID is valid, False otherwise.
    
    Validation Criteria:
    1. Must be a non-empty string
    2. Must be a valid UUID (v4)
    3. Cannot be all whitespace
    """
    # Check if input is a string and not empty
    if not isinstance(transaction_id, str):
        return False
    
    # Trim whitespace and check if non-empty
    if not transaction_id.strip():
        return False
    
    # Validate UUID v4 format
    try:
        # Attempt to parse the transaction ID as a UUID
        parsed_uuid = uuid.UUID(transaction_id, version=4)
        
        # Check if the parsed UUID matches the original input
        return str(parsed_uuid) == transaction_id
    except (ValueError, AttributeError):
        return False