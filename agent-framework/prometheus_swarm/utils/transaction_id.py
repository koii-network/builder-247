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
    2. Must be a valid UUID
    3. Cannot contain whitespace
    """
    if not isinstance(transaction_id, str):
        return False
    
    # Check for empty string
    if not transaction_id.strip():
        return False
    
    # Check for whitespace
    if re.search(r'\s', transaction_id):
        return False
    
    # Check if it's a valid UUID
    try:
        uuid.UUID(transaction_id)
        return True
    except ValueError:
        return False