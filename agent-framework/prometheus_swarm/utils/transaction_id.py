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

    # Extract potential UUID using regex
    uuid_match = re.search(r'([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})', cleaned_id, re.IGNORECASE)
    
    if uuid_match:
        extracted_uuid = uuid_match.group(1)
        try:
            # Validate extracted UUID
            uuid.UUID(extracted_uuid)
            return extracted_uuid
        except ValueError:
            return None

    # If no UUID found, validate entire string
    try:
        uuid.UUID(cleaned_id)
        return cleaned_id
    except ValueError:
        return None