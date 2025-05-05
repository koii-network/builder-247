import re
import uuid

def validate_transaction_id(transaction_id: str) -> bool:
    """
    Validate a transaction ID based on the following criteria:
    1. Must be a non-empty string
    2. Must be a valid UUID
    3. UUID must be version 4 (random)
    4. Must not contain invalid characters

    Args:
        transaction_id (str): The transaction ID to validate

    Returns:
        bool: True if the transaction ID is valid, False otherwise
    """
    # Check if input is a string and not empty
    if not isinstance(transaction_id, str) or not transaction_id:
        return False

    # Remove any whitespace from the start or end
    transaction_id = transaction_id.strip()

    # Validate UUID format
    try:
        # Attempt to create a UUID object
        parsed_uuid = uuid.UUID(transaction_id, version=4)
        
        # Verify that the parsed UUID matches the input exactly
        return str(parsed_uuid) == transaction_id
    except (ValueError, AttributeError):
        return False