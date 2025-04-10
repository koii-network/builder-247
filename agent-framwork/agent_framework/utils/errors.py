"""Error type for API errors."""


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
