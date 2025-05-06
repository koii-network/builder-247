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
    1. Must be a string
    2. Must not be empty or whitespace
    3. Must match a specific UUID format
    4. Maximum length of 50 characters
    """
    # Check if input is a string
    if not isinstance(transaction_id, str):
        return False

    # Remove whitespace
    transaction_id = transaction_id.strip()

    # Check if empty
    if not transaction_id:
        return False

    # Check maximum length
    if len(transaction_id) > 50:
        return False

    # Validate UUID format (allows standard UUID formats)
    try:
        uuid.UUID(transaction_id)
        return True
    except ValueError:
        return False