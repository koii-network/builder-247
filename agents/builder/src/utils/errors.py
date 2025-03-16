"""Error type for pre-logged errors."""


class ClientAPIError(Exception):
    """Exception raised for API client errors."""

    def __init__(self, original_error):
        super().__init__(str(original_error))
        self.original_error = original_error
        # Try to get status code from different error types
        self.status_code = getattr(original_error, "status_code", None)
        if self.status_code is None:
            # Handle Anthropic errors
            if hasattr(original_error, "response") and hasattr(
                original_error.response, "status_code"
            ):
                self.status_code = original_error.response.status_code
            # Handle other API errors that might have status in different attributes
            elif hasattr(original_error, "status"):
                self.status_code = original_error.status
