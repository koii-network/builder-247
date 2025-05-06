import re
from typing import Union, Optional

def validate_transaction_id(transaction_id: Union[str, int, None]) -> Optional[str]:
    """
    Validate a transaction ID with the following constraints:
    1. Must not be None
    2. Must be a non-empty string or convertible to a string
    3. Must contain only alphanumeric characters
    4. Length between 10 and 100 characters

    Args:
        transaction_id (Union[str, int, None]): The transaction ID to validate

    Returns:
        Optional[str]: The validated transaction ID or None if invalid

    Raises:
        TypeError: If the input is not a string, integer, or None
    """
    # Check if transaction_id is None
    if transaction_id is None:
        return None

    # Convert to string if it's an integer
    if isinstance(transaction_id, int):
        transaction_id = str(transaction_id)

    # Validate input type
    if not isinstance(transaction_id, str):
        raise TypeError("Transaction ID must be a string, integer, or None")

    # Remove any whitespace
    transaction_id = transaction_id.strip()

    # Check length constraints
    if len(transaction_id) < 10 or len(transaction_id) > 100:
        return None

    # Check if contains only alphanumeric characters
    if not re.match(r'^[a-zA-Z0-9]+$', transaction_id):
        return None

    return transaction_id