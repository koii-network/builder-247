"""Error types for API and Nonce related errors."""

import logging
from typing import Optional, Dict, Any


class ClientAPIError(Exception):
    """Error for API calls with status code."""

    def __init__(self, original_error: Exception):
        print(original_error)
        if hasattr(original_error, "status_code"):
            self.status_code = original_error.status_code
        else:
            self.status_code = 500
        if hasattr(original_error, "message"):
            super().__init__(original_error.message)
        else:
            super().__init__(str(original_error))


class NonceError(Exception):
    """Custom exception for Nonce-related errors."""

    def __init__(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        log_level: int = logging.ERROR
    ):
        """
        Initialize a NonceError with detailed information.

        Args:
            message (str): Error description
            context (dict, optional): Additional context about the error
            log_level (int, optional): Logging level for the error
        """
        super().__init__(message)
        self.context = context or {}
        
        # Setup logging
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)
        
        # Log the error with context
        log_method = {
            logging.DEBUG: logger.debug,
            logging.INFO: logger.info,
            logging.WARNING: logger.warning,
            logging.ERROR: logger.error,
            logging.CRITICAL: logger.critical
        }.get(log_level, logger.error)
        
        log_message = f"NonceError: {message}"
        if self.context:
            log_message += f" | Context: {self.context}"
        
        log_method(log_message)


def validate_nonce(nonce: Any, expected_type: type = int, min_value: Optional[int] = None) -> None:
    """
    Validate nonce value with comprehensive checks.

    Args:
        nonce (Any): Nonce value to validate
        expected_type (type, optional): Expected type of nonce. Defaults to int.
        min_value (int, optional): Minimum allowed value for the nonce

    Raises:
        NonceError: If nonce is invalid
    """
    if nonce is None:
        raise NonceError("Nonce cannot be None", {"provided_nonce": nonce})
    
    if not isinstance(nonce, expected_type):
        raise NonceError(
            f"Invalid nonce type. Expected {expected_type.__name__}, got {type(nonce).__name__}",
            {"provided_nonce": nonce, "expected_type": expected_type.__name__}
        )
    
    if min_value is not None and nonce < min_value:
        raise NonceError(
            f"Nonce value too small. Must be >= {min_value}",
            {"provided_nonce": nonce, "min_value": min_value}
        )