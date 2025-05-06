"""Extended error types for various application errors, including nonce handling."""

from typing import Optional, Any


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
    """
    Custom exception for nonce-related errors in API and cryptographic operations.

    Attributes:
        message (str): Descriptive error message
        context (dict): Additional context about the nonce error
        error_type (str): Specific type of nonce error
    """

    def __init__(
        self,
        message: str,
        error_type: str = "NONCE_ERROR",
        context: Optional[dict] = None
    ):
        """
        Initialize a NonceError with detailed error information.

        Args:
            message (str): A human-readable description of the error
            error_type (str, optional): Categorization of the nonce error. Defaults to "NONCE_ERROR"
            context (dict, optional): Additional contextual information about the error
        """
        self.message = message
        self.error_type = error_type
        self.context = context or {}
        super().__init__(self._format_error())

    def _format_error(self) -> str:
        """
        Format the error message with type and context.

        Returns:
            str: A comprehensive error description
        """
        error_details = f"[{self.error_type}] {self.message}"
        if self.context:
            context_str = " | ".join(f"{k}: {v}" for k, v in self.context.items())
            error_details += f" || Context: {context_str}"
        return error_details

    def log_error(self, logger=None):
        """
        Log the error using the provided logger or print to console.

        Args:
            logger (Optional[logging.Logger]): Logger to use. If None, prints to console.
        """
        error_log = self._format_error()
        if logger:
            logger.error(error_log)
        else:
            print(f"ERROR: {error_log}")

    @classmethod
    def raise_for_invalid_nonce(
        cls,
        nonce: Any,
        expected_type: type = int,
        min_value: Optional[int] = None,
        max_value: Optional[int] = None
    ):
        """
        Validate a nonce and raise an error if it's invalid.

        Args:
            nonce (Any): The nonce to validate
            expected_type (type, optional): Expected type of the nonce. Defaults to int.
            min_value (Optional[int]): Minimum allowed nonce value
            max_value (Optional[int]): Maximum allowed nonce value

        Raises:
            NonceError: If the nonce is invalid
        """
        context = {
            "nonce": str(nonce),
            "expected_type": expected_type.__name__,
            "min_value": min_value,
            "max_value": max_value
        }

        # Type check
        if not isinstance(nonce, expected_type):
            raise cls(
                f"Invalid nonce type: expected {expected_type.__name__}",
                error_type="NONCE_TYPE_ERROR",
                context=context
            )

        # Value range checks
        if min_value is not None and nonce < min_value:
            raise cls(
                f"Nonce value too low: must be >= {min_value}",
                error_type="NONCE_VALUE_TOO_LOW",
                context=context
            )

        if max_value is not None and nonce > max_value:
            raise cls(
                f"Nonce value too high: must be <= {max_value}",
                error_type="NONCE_VALUE_TOO_HIGH",
                context=context
            )