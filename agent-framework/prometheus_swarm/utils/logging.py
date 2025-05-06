"""Centralized logging configuration and utilities."""

import logging
import sys
import traceback
from typing import Any, Optional, Dict
from pathlib import Path
from functools import wraps
import json
from colorama import init, Fore, Style

# Rest of the existing logging code remains the same
# ... [keep all existing code from previous implementation] ...

def log_error_details(
    error: Exception,
    context: Optional[str] = None,
    include_traceback: bool = True,
    log_func: Optional[callable] = None
) -> None:
    """
    Enhanced error logging with detailed context and optional custom logging.

    Args:
        error: The exception to log
        context: Optional context description for the error
        include_traceback: Whether to include full stack trace
        log_func: Optional custom logging function
    """
    if not _logging_configured:
        configure_logging()

    # Use the provided log_func or default to logger.error
    error_log = log_func or logger.error

    # Log section header
    error_log(f"\n=== {context.upper() if context else 'ERROR'} ===")

    # Log error type and message
    error_log(f"Error Type: {type(error).__name__}")
    error_log(f"Error Message: {str(error)}")

    # Log additional context if available (for our custom error types)
    if hasattr(error, 'context') and error.context:
        error_log("Error Context:")
        try:
            error_log(json.dumps(error.context, indent=2))
        except Exception:
            error_log(str(error.context))

    # Include traceback if requested
    if include_traceback:
        error_log("Stack Trace:")
        for line in traceback.format_exc().splitlines():
            error_log(line)

def log_with_timing(func):
    """
    Decorator to log function execution with timing and error handling.

    Provides detailed logging for function entry, successful execution,
    and potential errors.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not _logging_configured:
            configure_logging()

        import time
        start_time = time.time()
        
        # Log function entry with arguments
        logger.info(f"Entering function: {func.__name__}")
        logger.info(f"Arguments: {args}, Keyword Arguments: {kwargs}")

        try:
            result = func(*args, **kwargs)
            
            # Log successful execution
            execution_time = time.time() - start_time
            logger.info(f"{func.__name__} executed successfully in {execution_time:.2f} seconds")
            
            return result
        
        except Exception as e:
            # Log detailed error information
            execution_time = time.time() - start_time
            log_error_details(
                e, 
                context=f"Function Execution Failed: {func.__name__}",
                include_traceback=True
            )
            logger.error(f"Function {func.__name__} failed after {execution_time:.2f} seconds")
            
            # Re-raise the exception to allow further error handling
            raise

    return wrapper