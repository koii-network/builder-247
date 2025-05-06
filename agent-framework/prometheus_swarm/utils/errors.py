"""Custom error types for Prometheus Swarm framework."""

class ConfigurationError(Exception):
    """Raised when a configuration issue is encountered."""
    
    def __init__(self, message, context=None):
        """
        Initialize configuration error.
        
        Args:
            message (str): Error description
            context (dict, optional): Additional error context
        """
        super().__init__(message)
        self.context = context or {}

class AuthenticationError(Exception):
    """Raised when authentication fails."""
    pass

class ResourceNotFoundError(Exception):
    """Raised when a requested resource cannot be found."""
    pass