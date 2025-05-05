import re
import uuid

def validate_transaction_id(transaction_id: str) -> bool:
    """
    Validate a transaction ID based on specific criteria.
    
    Args:
        transaction_id (str): The transaction ID to validate.
    
    Returns:
        bool: True if the transaction ID is valid, False otherwise.
    
    Validation criteria:
    1. Must be a non-empty string
    2. Must be a valid UUID (version 4)
    3. Must not be longer than 36 characters
    4. Must contain only hexadecimal characters and hyphens
    """
    # Check if input is None or empty
    if not transaction_id:
        return False
    
    # Check length 
    if len(transaction_id) > 36:
        return False
    
    # Validate UUID v4 format using regex
    uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$'
    
    # Check if transaction_id matches UUID v4 pattern
    if not re.match(uuid_pattern, transaction_id, re.IGNORECASE):
        return False
    
    # Additional check: try to parse as UUID
    try:
        parsed_uuid = uuid.UUID(transaction_id, version=4)
        return True
    except ValueError:
        return False