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
    2. Must be a valid UUID (version 4)
    3. Must not be an empty or whitespace-only string
    """
    # Check if transaction_id is a string and not empty or whitespace
    if not isinstance(transaction_id, str) or not transaction_id.strip():
        return False

    # Use UUID validation to ensure it's a valid v4 UUID
    try:
        # Validate UUID format and version
        parsed_uuid = uuid.UUID(transaction_id, version=4)
        return str(parsed_uuid) == transaction_id
    except (ValueError, AttributeError):
        return False