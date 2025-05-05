import re
import uuid
from typing import Union, Optional

def validate_transaction_id(transaction_id: Union[str, None]) -> bool:
    """
    Validate a transaction ID based on the following criteria:
    1. Cannot be None
    2. Must be a string
    3. Must be a valid UUID (v4)
    4. Must not be an empty string
    5. Matches UUID v4 format

    Args:
        transaction_id (Union[str, None]): The transaction ID to validate

    Returns:
        bool: True if the transaction ID is valid, False otherwise
    """
    # Check for None
    if transaction_id is None:
        return False

    # Check if it's a string
    if not isinstance(transaction_id, str):
        return False

    # Check for empty string
    if not transaction_id.strip():
        return False

    # Use UUID validation to ensure it's a valid v4 UUID
    try:
        uuid_obj = uuid.UUID(transaction_id, version=4)
        # Additional check to ensure the UUID matches the exact v4 format
        return str(uuid_obj) == transaction_id
    except (ValueError, AttributeError):
        return False

def generate_transaction_id() -> str:
    """
    Generate a new unique transaction ID using UUID v4.

    Returns:
        str: A new transaction ID
    """
    return str(uuid.uuid4())