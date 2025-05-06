"""
Module for transaction ID constraint validation.

This module provides utilities to validate transaction IDs based on 
specified constraints.
"""

import re
import uuid


def validate_transaction_id(transaction_id: str) -> bool:
    """
    Validate a transaction ID based on standard constraints.

    Args:
        transaction_id (str): The transaction ID to validate.

    Returns:
        bool: True if the transaction ID is valid, False otherwise.

    Constraints:
    1. Must be a valid UUID (v4)
    2. Cannot be empty or None
    3. Must contain only hexadecimal characters and hyphens
    4. Total length should be 36 characters
    """
    if not transaction_id:
        return False

    # Check if it's a valid UUID v4
    try:
        # Validate UUID parsing and structure
        parsed_uuid = uuid.UUID(transaction_id, version=4)
        
        # Additional regex validation for extra strictness
        uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$'
        return bool(re.match(uuid_pattern, str(parsed_uuid).lower()))
    
    except (ValueError, AttributeError):
        return False