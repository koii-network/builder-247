import re
import uuid

def validate_transaction_id(transaction_id: str) -> bool:
    """
    Validate a transaction ID based on specific criteria.

    Args:
        transaction_id (str): The transaction ID to validate.

    Returns:
        bool: True if the transaction ID is valid, False otherwise.
    """
    if not isinstance(transaction_id, str):
        return False

    # Check length (assuming valid transaction IDs are between 10 and 50 characters)
    if len(transaction_id) < 10 or len(transaction_id) > 50:
        return False

    # Check for alphanumeric characters and allowed special characters
    if not re.match(r'^[a-zA-Z0-9_\-\.]+$', transaction_id):
        return False

    # Optional: Additional validation like checking UUID format
    try:
        uuid.UUID(transaction_id)
        return True
    except ValueError:
        # Not a UUID, but still can be a valid transaction ID
        return True