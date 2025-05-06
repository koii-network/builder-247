import re
from typing import Union

def validate_transaction_id(transaction_id: Union[str, None]) -> bool:
    """
    Validate a transaction ID based on specific constraints.

    Args:
        transaction_id (Union[str, None]): The transaction ID to validate.

    Returns:
        bool: True if the transaction ID is valid, False otherwise.

    Validation rules:
    - Must not be None
    - Must be a non-empty string
    - Must be alphanumeric
    - Must be between 10 and 50 characters long
    - Cannot start or end with a hyphen or underscore
    """
    # Check if transaction_id is None
    if transaction_id is None:
        return False
    
    # Check if transaction_id is a non-empty string
    if not isinstance(transaction_id, str) or len(transaction_id) == 0:
        return False
    
    # Check length constraints
    if len(transaction_id) < 10 or len(transaction_id) > 50:
        return False
    
    # Check if transaction_id contains only valid characters
    # Allows alphanumeric characters, hyphens, and underscores, 
    # but cannot start or end with a hyphen or underscore
    pattern = r'^[a-zA-Z0-9](?:[a-zA-Z0-9-_]*[a-zA-Z0-9])?$'
    
    return bool(re.match(pattern, transaction_id))