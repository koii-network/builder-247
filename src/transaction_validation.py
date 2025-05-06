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
    1. Must be a non-empty string
    2. Must be exactly 36 characters long (standard UUID format)
    3. Must be a valid UUID (standard UUID v4 format)
    4. Cannot contain any whitespace
    """
    # Check if input is a string and not empty
    if not isinstance(transaction_id, str) or not transaction_id:
        return False

    # Check length (standard UUID is 36 characters)
    if len(transaction_id) != 36:
        return False

    # Check for whitespace
    if re.search(r'\s', transaction_id):
        return False

    # Validate UUID format
    try:
        # Try to parse the transaction_id as a UUID
        uuid_obj = uuid.UUID(transaction_id, version=4)
        
        # Check if the parsed UUID matches the original input
        return str(uuid_obj) == transaction_id
    except ValueError:
        return False