"""Error type for pre-logged errors."""


class ClientAPIError(Exception):
    """Exception raised for API client errors."""

    def __init__(self, original_error):
        # Extract error details
        error_dict = self._extract_error_details(original_error)
        self.status_code = error_dict["status_code"]
        self.error_type = error_dict["error_type"]
        self.message = error_dict["message"]

        # Format error message
        super().__init__(f"Error code: {self.status_code} - {self.message}")
        self.original_error = original_error

    def _extract_error_details(self, error):
        """Extract error details from various error types."""
        details = {"status_code": None, "error_type": "unknown", "message": str(error)}

        # Handle Anthropic error format
        if hasattr(error, "response"):
            if hasattr(error.response, "json"):
                try:
                    error_json = error.response.json()
                    if isinstance(error_json, dict):
                        error_obj = error_json.get("error", {})
                        details["error_type"] = error_obj.get("type", "unknown")
                        details["message"] = error_obj.get("message", str(error))
                except Exception:
                    pass
            details["status_code"] = getattr(error.response, "status_code", None)

        # Direct status_code attribute
        if details["status_code"] is None and hasattr(error, "status_code"):
            details["status_code"] = error.status_code

        # Status attribute
        if details["status_code"] is None and hasattr(error, "status"):
            details["status_code"] = error.status

        # Default to 500 if no status code found
        if details["status_code"] is None:
            details["status_code"] = 500

        return details

    def is_retryable(self):
        """Determine if this error should be retried."""
        # Don't retry client errors (except rate limits)
        if self.status_code == 429:  # Rate limit
            return True
        if self.status_code < 500:  # Other client errors
            return False
        return True  # Retry all server errors
