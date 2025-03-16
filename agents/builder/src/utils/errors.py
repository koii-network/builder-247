"""Error type for pre-logged errors."""


class ClientAPIError(Exception):
    """Exception raised for API client errors."""

    def __init__(self, original_error):
        super().__init__(str(original_error))
        self.original_error = original_error
        self.status_code = self._extract_status_code(original_error)

    def _extract_status_code(self, error):
        """Extract status code from various error types."""
        # Direct status_code attribute
        if hasattr(error, "status_code"):
            return error.status_code

        # Response object with status_code
        if hasattr(error, "response") and hasattr(error.response, "status_code"):
            return error.response.status_code

        # Status attribute
        if hasattr(error, "status"):
            return error.status

        # Default to 500 if no status code found
        return 500  # Treat unknown errors as server errors by default
