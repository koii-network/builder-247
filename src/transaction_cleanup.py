import re
import uuid

def clean_transaction_id(transaction_id: str) -> str:
    """
    Clean and validate a transaction ID.
    
    Args:
        transaction_id (str): The transaction ID to clean.
    
    Returns:
        str: A standardized, cleaned transaction ID.
    
    Raises:
        ValueError: If the transaction ID is invalid or cannot be cleaned.
    """
    # Check if input is None or empty
    if not transaction_id:
        raise ValueError("Transaction ID cannot be empty")
    
    # Remove leading/trailing whitespace
    cleaned_id = transaction_id.strip()
    
    # Remove any non-alphanumeric characters except hyphens
    cleaned_id = re.sub(r'[^a-zA-Z0-9-]', '', cleaned_id)
    
    # Convert to lowercase
    cleaned_id = cleaned_id.lower()
    
    # Truncate to a reasonable length (e.g., 50 characters)
    cleaned_id = cleaned_id[:50]
    
    # If the cleaned ID is empty after processing, generate a new UUID
    if not cleaned_id:
        cleaned_id = str(uuid.uuid4())
    
    return cleaned_id