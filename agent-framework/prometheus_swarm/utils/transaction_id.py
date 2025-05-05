import uuid
import re
from typing import Union, Optional

def cleanup_transaction_id(transaction_id: Union[str, uuid.UUID]) -> Optional[str]:
    """
    Clean up and validate a transaction ID.

    Args:
        transaction_id (Union[str, uuid.UUID]): The transaction ID to clean up.

    Returns:
        Optional[str]: A cleaned and validated transaction ID, or None if invalid.

    Raises:
        TypeError: If the input is not a string or UUID.
    """
    # Handle UUID input
    if isinstance(transaction_id, uuid.UUID):
        return str(transaction_id)

    # Validate input type
    if not isinstance(transaction_id, str):
        raise TypeError("Transaction ID must be a string or UUID")

    # Remove whitespace
    cleaned_id = transaction_id.strip()

    # Remove non-alphanumeric characters except hyphens
    cleaned_id = re.sub(r'[^a-zA-Z0-9\-]', '', cleaned_id)

    # Validate UUID format (optional extra validation)
    try:
        uuid.UUID(cleaned_id)
        return cleaned_id
    except ValueError:
        return None