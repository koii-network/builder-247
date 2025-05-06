"""Transaction ID validation utility."""

import re
import uuid

def validate_transaction_id(transaction_id: str) -> bool:
    """
    Validate a transaction ID with the following constraints:
    1. Must be a valid UUID
    2. Cannot be empty or None
    3. Must be a string

    Args:
        transaction_id (str): The transaction ID to validate

    Returns:
        bool: True if the transaction ID is valid, False otherwise
    """
    if not transaction_id or not isinstance(transaction_id, str):
        return False

    try:
        # Attempt to parse as UUID
        uuid.UUID(transaction_id)
        return True
    except ValueError:
        return False