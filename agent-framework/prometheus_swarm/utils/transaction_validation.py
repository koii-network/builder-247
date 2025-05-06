"""
Utility functions for transaction ID constraint validation.
"""
import re
import uuid

def validate_transaction_id(transaction_id: str) -> bool:
    """
    Validate a transaction ID based on specific constraints.

    Args:
        transaction_id (str): The transaction ID to validate.

    Returns:
        bool: True if the transaction ID is valid, False otherwise.

    Constraints:
    1. Must be a valid UUID
    2. Cannot be an empty string
    3. Must be exactly 36 characters long (standard UUID format)
    4. Must not contain only whitespace
    """
    if not transaction_id or not isinstance(transaction_id, str):
        return False

    # Remove leading/trailing whitespace
    transaction_id = transaction_id.strip()

    # Check length
    if len(transaction_id) != 36:
        return False

    # Validate UUID format using regex
    uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
    if not re.match(uuid_pattern, transaction_id, re.IGNORECASE):
        return False

    # Additional validation: try parsing as UUID
    try:
        uuid.UUID(transaction_id)
        return True
    except ValueError:
        return False