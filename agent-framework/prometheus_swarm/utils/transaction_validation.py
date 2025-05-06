import re
from typing import Optional, Union

def validate_transaction_id(transaction_id: Optional[Union[str, int, float]]) -> bool:
    """
    Validate a transaction ID based on specific constraints.

    Args:
        transaction_id (Optional[Union[str, int, float]]): The transaction ID to validate.

    Returns:
        bool: True if the transaction ID is valid, False otherwise.

    Validation rules:
    1. Must not be None
    2. Must be a non-empty string or a positive integer
    3. If a string, must only contain alphanumeric characters
    4. Must not exceed 50 characters in length
    """
    # Check if transaction_id is None
    if transaction_id is None:
        return False

    # Reject non-string, non-integer types
    if not isinstance(transaction_id, (str, int, float)):
        return False

    # Convert to string for consistent validation
    str_transaction_id = str(transaction_id)

    # Check length
    if len(str_transaction_id) == 0 or len(str_transaction_id) > 50:
        return False

    # Reject floating point numbers
    if isinstance(transaction_id, float):
        return False

    # If original input was an integer, ensure it's positive
    if isinstance(transaction_id, int) and transaction_id <= 0:
        return False

    # If it's a string, check for alphanumeric characters
    if isinstance(transaction_id, str):
        return bool(re.match(r'^[a-zA-Z0-9]+$', str_transaction_id))

    return True