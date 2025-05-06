from typing import List, Union

class TransactionIDDuplicateError(Exception):
    """Raised when a duplicate transaction ID is detected."""
    pass

def check_transaction_id_duplicates(transaction_ids: List[str]) -> List[str]:
    """
    Check for duplicate transaction IDs and return a list of duplicates.

    Args:
        transaction_ids (List[str]): A list of transaction IDs to check for duplicates.

    Returns:
        List[str]: A list of duplicate transaction IDs.

    Raises:
        TypeError: If the input is not a list of strings.
        ValueError: If any transaction ID is an empty string.
    """
    # Validate input
    if not isinstance(transaction_ids, list):
        raise TypeError("Input must be a list of transaction IDs")
    
    if not all(isinstance(tid, str) for tid in transaction_ids):
        raise TypeError("All transaction IDs must be strings")
    
    if any(tid.strip() == '' for tid in transaction_ids):
        raise ValueError("Transaction IDs cannot be empty strings")

    # Find duplicates using set logic
    seen = set()
    duplicates = set()
    
    for tid in transaction_ids:
        if tid in seen:
            duplicates.add(tid)
        else:
            seen.add(tid)
    
    return list(duplicates)

def validate_transaction_ids(transaction_ids: List[str]) -> None:
    """
    Validate transaction IDs, raising an exception if duplicates are found.

    Args:
        transaction_ids (List[str]): A list of transaction IDs to validate.

    Raises:
        TransactionIDDuplicateError: If duplicate transaction IDs are detected.
        TypeError: If the input is not a list of strings.
        ValueError: If any transaction ID is an empty string.
    """
    duplicates = check_transaction_id_duplicates(transaction_ids)
    
    if duplicates:
        raise TransactionIDDuplicateError(f"Duplicate transaction IDs found: {duplicates}")