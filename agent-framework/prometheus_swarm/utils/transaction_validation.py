import uuid
import re
from typing import Union

def validate_transaction_id(transaction_id: Union[str, None]) -> bool:
    """
    Validate a transaction ID based on the following criteria:
    1. Must not be None
    2. Must be a non-empty string
    3. Must be a valid UUID v4 format
    4. Must not contain invalid characters

    Args:
        transaction_id (Union[str, None]): The transaction ID to validate

    Returns:
        bool: True if the transaction ID is valid, False otherwise
    """
    # Check if transaction_id is None
    if transaction_id is None:
        return False
    
    # Check if transaction_id is an empty string
    if not isinstance(transaction_id, str) or len(transaction_id.strip()) == 0:
        return False
    
    # Validate UUID v4 format using regex
    uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$'
    
    try:
        # First, try to validate the format with regex
        if not re.match(uuid_pattern, transaction_id.lower()):
            return False
        
        # Then validate it can be parsed as a valid UUID v4
        parsed_uuid = uuid.UUID(transaction_id, version=4)
        
        return True
    except (ValueError, AttributeError):
        return False