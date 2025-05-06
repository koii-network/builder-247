"""Error types for various API and nonce-related errors."""

import logging

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
    """Error raised for nonce-related issues in cryptographic operations."""

    def __init__(self, message: str, error_type: str = 'unknown'):
        """
        Initialize a NonceError with details about the nonce issue.

        Args:
            message (str): Description of the nonce error
            error_type (str, optional): Type of nonce error. Defaults to 'unknown'.
        """
        self.error_type = error_type
        self.timestamp = logging.Formatter('%(asctime)s').formatTime(logging.LogRecord(
            name='', level=logging.ERROR, pathname='', lineno=0,
            msg='', args=(), exc_info=None
        ))
        super().__init__(f"Nonce Error [{error_type}]: {message}")

        # Log the nonce error
        logging.getLogger(__name__).error(
            f"Nonce Error [{error_type}]: {message} at {self.timestamp}"
        )

class NonceReplayError(NonceError):
    """Specific error for replay attacks or duplicate nonce usage."""

    def __init__(self, message: str):
        super().__init__(message, error_type='replay_attack')

class NonceExpirationError(NonceError):
    """Specific error for nonce expiration."""

    def __init__(self, message: str):
        super().__init__(message, error_type='expired_nonce')