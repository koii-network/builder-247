"""Logging utilities for transaction ID cleanup operations."""

from typing import List, Dict, Any
from .logging import logger, log_section, log_key_value

def log_transaction_cleanup(
    transaction_ids: List[str], 
    cleanup_method: str, 
    additional_context: Dict[str, Any] = None
) -> None:
    """
    Log transaction ID cleanup details with comprehensive information.

    Args:
        transaction_ids (List[str]): List of transaction IDs being cleaned up
        cleanup_method (str): Method used for transaction ID cleanup
        additional_context (Dict[str, Any], optional): Extra context for the cleanup operation
    """
    log_section("Transaction ID Cleanup")
    
    # Log basic cleanup information
    log_key_value("Cleanup Method", cleanup_method)
    log_key_value("Total Transactions", len(transaction_ids))
    
    # Log transaction IDs
    if len(transaction_ids) <= 10:
        log_key_value("Transaction IDs", transaction_ids)
    else:
        log_key_value("First 5 Transaction IDs", transaction_ids[:5])
        log_key_value("Last 5 Transaction IDs", transaction_ids[-5:])
    
    # Log additional context if provided
    if additional_context:
        log_section("Cleanup Context")
        for key, value in additional_context.items():
            log_key_value(key, value)

def log_transaction_cleanup_error(
    transaction_ids: List[str], 
    cleanup_method: str, 
    error: Exception
) -> None:
    """
    Log an error that occurred during transaction ID cleanup.

    Args:
        transaction_ids (List[str]): List of transaction IDs that failed cleanup
        cleanup_method (str): Method used for transaction ID cleanup
        error (Exception): The exception that occurred
    """
    log_section("Transaction ID Cleanup Error")
    log_key_value("Cleanup Method", cleanup_method)
    log_key_value("Failed Transactions", len(transaction_ids))
    
    # Log the first few transaction IDs
    if len(transaction_ids) <= 5:
        log_key_value("Transaction IDs", transaction_ids)
    else:
        log_key_value("First 5 Transaction IDs", transaction_ids[:5])
    
    # Log the error details
    logger.error(f"Error: {str(error)}")