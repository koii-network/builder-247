"""Error type for pre-logged errors."""


class ClientAPIError(Exception):
    """Error that has already been logged at source.

    Used to wrap API errors that have been logged where they occurred,
    to prevent duplicate logging higher up the stack.
    """

    def __init__(self, original_error: Exception):
        self.original_error = original_error
        super().__init__(str(original_error))

    @property
    def status_code(self) -> int:
        """Preserve status code from original error if it exists."""
        return getattr(self.original_error, "status_code", None)
