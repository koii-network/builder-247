import re
from typing import Union

def validate_transaction_id(transaction_id: Union[str, int]) -> bool:
    """
    Validate a transaction ID to ensure it meets specific constraints.
    
    Args:
        transaction_id (Union[str, int]): The transaction ID to validate.
    
    Returns:
        bool: True if the transaction ID is valid, False otherwise.
    
    Validation Constraints:
    - Must be convertible to a string
    - Must not be empty or None
    - Must contain only alphanumeric characters
    - Must be between 8 and 64 characters long
    """
    # Convert to string and handle None
    if transaction_id is None:
        return False
    
    # Convert to string 
    try:
        str_id = str(transaction_id).strip()
    except Exception:
        return False
    
    # Check length constraints
    if len(str_id) < 8 or len(str_id) > 64:
        return False
    
    # Check for alphanumeric characters only
    if not re.match(r'^[a-zA-Z0-9]+$', str_id):
        return False
    
    return True