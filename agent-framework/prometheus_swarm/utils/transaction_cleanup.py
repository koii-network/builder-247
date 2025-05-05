import re
from typing import Union, List, Optional

def clean_transaction_id(transaction_id: Union[str, int]) -> Optional[str]:
    """
    Clean and standardize a transaction ID.

    Args:
        transaction_id (Union[str, int]): The transaction ID to clean.

    Returns:
        Optional[str]: A cleaned and standardized transaction ID, or None if invalid.

    Processes:
    - Convert to string
    - Remove whitespace
    - Convert to lowercase
    - Remove any non-alphanumeric characters
    - Truncate to a maximum length of 50 characters
    """
    if transaction_id is None:
        return None

    # Convert to string and strip whitespace
    cleaned_id = str(transaction_id).strip().lower()

    # Remove non-alphanumeric characters
    cleaned_id = re.sub(r'[^a-z0-9]', '', cleaned_id)

    # Truncate to 50 characters
    cleaned_id = cleaned_id[:50]

    # Return None if result is empty
    return cleaned_id if cleaned_id else None

def cleanup_transaction_ids(transaction_ids: Union[str, int, List[Union[str, int]]]) -> List[str]:
    """
    Clean multiple transaction IDs.

    Args:
        transaction_ids (Union[str, int, List[Union[str, int]]]): Transaction ID or list of transaction IDs to clean.

    Returns:
        List[str]: List of cleaned transaction IDs.

    Removes None values and duplicates.
    """
    # Normalize input to list
    if not isinstance(transaction_ids, list):
        transaction_ids = [transaction_ids]

    # Clean and filter transaction IDs
    cleaned_ids = [
        cleaned_id for id in transaction_ids 
        if (cleaned_id := clean_transaction_id(id)) is not None
    ]

    # Remove duplicates while preserving order
    return list(dict.fromkeys(cleaned_ids))