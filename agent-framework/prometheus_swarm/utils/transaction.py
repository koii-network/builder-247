import re
import uuid

def validate_transaction_id(transaction_id: str) -> bool:
    """
    Validate a transaction ID based on the following criteria:
    1. Must be a valid UUID
    2. Cannot be empty or None
    3. Cannot contain invalid characters

    Args:
        transaction_id (str): The transaction ID to validate

    Returns:
        bool: True if the transaction ID is valid, False otherwise
    """
    # Check if transaction_id is None or empty
    if not transaction_id:
        return False

    # Check if the transaction_id is a valid UUID
    try:
        # Convert the input to a UUID, which will validate its format
        uuid.UUID(str(transaction_id))
        return True
    except (ValueError, TypeError):
        return False