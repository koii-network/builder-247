"""
Transaction ID Time Window Configuration Module.

This module provides functionality to configure and manage
transaction ID time window settings.
"""

from typing import Optional, Dict, Any
import time


class TransactionIDTimeWindowError(Exception):
    """Custom exception for Transaction ID Time Window configuration errors."""
    pass


def configure_transaction_id_time_window(
    window_duration: int = 3600,  # Default 1 hour
    max_transactions: Optional[int] = None,
    allow_overlapping: bool = False
) -> Dict[str, Any]:
    """
    Configure transaction ID time window settings.

    Args:
        window_duration (int): Duration of the time window in seconds. Defaults to 3600 (1 hour).
        max_transactions (Optional[int]): Maximum number of transactions allowed in the window.
            If None, no limit is imposed. Defaults to None.
        allow_overlapping (bool): Whether transactions with same ID can overlap. Defaults to False.

    Returns:
        Dict[str, Any]: Configuration settings for transaction ID time window.

    Raises:
        TransactionIDTimeWindowError: If invalid configuration is provided.
    """
    # Validate window duration
    if window_duration <= 0:
        raise TransactionIDTimeWindowError("Window duration must be a positive integer.")

    # Validate max transactions
    if max_transactions is not None and max_transactions <= 0:
        raise TransactionIDTimeWindowError("Max transactions must be a positive integer or None.")

    config = {
        "window_duration": window_duration,
        "max_transactions": max_transactions,
        "allow_overlapping": allow_overlapping,
        "created_at": int(time.time())
    }

    return config