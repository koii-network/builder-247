"""
Module for transaction ID constraint validation.

This module provides utilities to validate transaction IDs based on 
specified constraints.
"""

import re


def validate_transaction_id(transaction_id: str) -> bool:
    """
    Validate a transaction ID based on standard constraints.

    Args:
        transaction_id (str): The transaction ID to validate.

    Returns:
        bool: True if the transaction ID is valid, False otherwise.

    Constraints:
    1. Must be a valid UUID v4
    2. Cannot be empty or None
    3. Must contain only hexadecimal characters and hyphens
    4. Total length should be 36 characters
    5. Specific version (4) and variant constraints
    """
    if not isinstance(transaction_id, str):
        return False

    # Strict UUID v4 regex pattern
    # Breakdown:
    # ^ start of string
    # [0-9a-f]{8} - 8 hex chars
    # -
    # [0-9a-f]{4} - 4 hex chars
    # -
    # 4[0-9a-f]{3} - version 4 with 3 hex chars
    # -
    # [89ab][0-9a-f]{3} - variant with 3 hex chars
    # -
    # [0-9a-f]{12} - 12 hex chars
    # $ end of string
    uuid_v4_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$'
    
    return bool(re.match(uuid_v4_pattern, transaction_id.lower()))