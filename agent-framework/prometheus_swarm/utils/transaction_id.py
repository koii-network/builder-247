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
    2. Must be a valid UUID (using strict validation)
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
    
    # Strict UUID format validation
    uuid_pattern = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', re.IGNORECASE)
    
    # Check if the transaction_id matches the UUID pattern
    if not uuid_pattern.match(transaction_id):
        return False
    
    # Additional validation to ensure a valid UUID
    try:
        parsed_uuid = uuid.UUID(transaction_id)
        return str(parsed_uuid) == transaction_id.lower()
    except ValueError:
        return False