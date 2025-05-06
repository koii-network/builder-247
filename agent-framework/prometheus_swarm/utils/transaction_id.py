import re
import uuid

def validate_transaction_id(transaction_id: str) -> bool:
    """
    Validate a transaction ID based on the following criteria:
    1. Must be a valid UUID (version 4)
    2. Cannot be an empty string
    3. Must match UUID regex pattern

    Args:
        transaction_id (str): The transaction ID to validate

    Returns:
        bool: True if the transaction ID is valid, False otherwise
    """
    # Check if transaction_id is None or empty
    if not transaction_id:
        return False

    # UUID regex pattern
    uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$'

    # Check if transaction_id matches UUID v4 pattern
    if not re.match(uuid_pattern, transaction_id, re.IGNORECASE):
        return False

    try:
        # Additional validation using uuid module
        parsed_uuid = uuid.UUID(transaction_id, version=4)
        return str(parsed_uuid) == transaction_id.lower()
    except ValueError:
        return False