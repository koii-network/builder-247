import re
import uuid

def validate_transaction_id(transaction_id: str) -> bool:
    """
    Validate a transaction ID based on the following criteria:
    1. Must be a valid UUID (versions 1, 3, 4, or 5)
    2. Cannot be an empty string
    3. Must be a string type

    Args:
        transaction_id (str): The transaction ID to validate

    Returns:
        bool: True if the transaction ID is valid, False otherwise
    """
    # Check if the input is a string and not empty
    if not isinstance(transaction_id, str) or not transaction_id:
        return False

    # Try to parse the UUID and validate its format
    try:
        # Attempt to convert the string to a UUID object
        parsed_uuid = uuid.UUID(transaction_id)
        
        # Check if the UUID version is 1, 3, 4, or 5
        return parsed_uuid.version in {1, 3, 4, 5}
    except (ValueError, AttributeError):
        # If conversion fails, it's not a valid UUID
        return False